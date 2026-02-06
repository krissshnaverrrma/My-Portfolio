import os
import json
import logging
import requests
from datetime import datetime
from .config import Config
from .database import (
    SessionLocal, Base, engine, APICache, Knowledge, BlogPost,
    Project, Skill, TimelineEvent, Service, ChatLog
)
logger = logging.getLogger(__name__)
_JSON_CACHE = None


def load_json_data(filename='data.json'):
    """Loads JSON data from file. Internal use; prefer get_data_json()."""
    global _JSON_CACHE
    if _JSON_CACHE:
        return _JSON_CACHE
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.exists(os.path.join(base_dir, filename)):
            base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, filename)
        with open(json_path, 'r', encoding='utf-8') as f:
            _JSON_CACHE = json.load(f)
            return _JSON_CACHE
    except FileNotFoundError:
        logger.error(f"❌ File not found: {filename}")
        return {}
    except Exception as e:
        logger.error(f"⚠️ Error Loading {filename}: {e}")
        return {}


def get_data_json():
    """Public accessor for cached JSON data."""
    return load_json_data()


def get_user_profile():
    """Returns the user_profile section from data.json."""
    return get_data_json().get("user_profile", {})


def get_ai_config():
    """Returns the ai_config section from data.json."""
    return get_data_json().get("ai_config", {})


def get_all_posts():
    db = SessionLocal()
    try:
        return db.query(BlogPost).order_by(BlogPost.created_at.desc()).all()
    finally:
        db.close()


def get_all_projects():
    db = SessionLocal()
    try:
        return db.query(Project).order_by(Project.is_featured.desc(), Project.id.asc()).all()
    finally:
        db.close()


def get_all_skills():
    db = SessionLocal()
    try:
        return db.query(Skill).all()
    finally:
        db.close()


def get_timeline(event_type):
    db = SessionLocal()
    try:
        return db.query(TimelineEvent).filter_by(type=event_type).all()
    finally:
        db.close()


def get_services():
    db = SessionLocal()
    try:
        return db.query(Service).all()
    finally:
        db.close()


def get_all_knowledge():
    db = SessionLocal()
    try:
        return db.query(Knowledge).all()
    finally:
        db.close()


def search_knowledge(user_query):
    """Smart Search: Checks if any database category exists in the user's input."""
    db = SessionLocal()
    try:
        all_entries = db.query(Knowledge).all()
        matches = []
        user_query = user_query.lower()
        for entry in all_entries:
            if entry.category.lower() in user_query:
                matches.append(entry)
            elif user_query in entry.info.lower() and len(user_query) > 3:
                matches.append(entry)
        return matches
    finally:
        db.close()


def log_conversation(session_id, u, b):
    db = SessionLocal()
    try:
        db.add(ChatLog(session_id=session_id, user_query=u, bot_response=b))
        db.commit()
    finally:
        db.close()


def get_chat_history(session_id, limit=10):
    db = SessionLocal()
    try:
        return db.query(ChatLog).filter_by(session_id=session_id)\
                 .order_by(ChatLog.timestamp.desc()).limit(limit).all()[::-1]
    finally:
        db.close()


class GitHubPortfolio:
    def __init__(self):
        self.username = Config.GITHUB_USERNAME
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if Config.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {Config.GITHUB_TOKEN}"
        self.cache_duration = 3600

    def _get_from_db(self, key):
        db = SessionLocal()
        try:
            entry = db.query(APICache).filter_by(key=key).first()
            if entry:
                age = (datetime.utcnow() - entry.timestamp).total_seconds()
                if age < self.cache_duration:
                    return json.loads(entry.data)
            return None
        except Exception as e:
            logger.error(f"⚠️ DB Cache Read Error: {e}")
            return None
        finally:
            db.close()

    def _save_to_db(self, key, data):
        db = SessionLocal()
        try:
            entry = db.query(APICache).filter_by(key=key).first()
            if entry:
                entry.data = json.dumps(data)
                entry.timestamp = datetime.utcnow()
            else:
                db.add(APICache(key=key, data=json.dumps(data)))
            db.commit()
        except Exception as e:
            logger.error(f"❌ DB Cache Save Error: {e}")
            db.rollback()
        finally:
            db.close()

    def get_profile(self):
        cache_key = "github_profile"
        cached_data = self._get_from_db(cache_key)
        if cached_data:
            return cached_data
        url = f"{self.base_url}/users/{self.username}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            profile_data = {
                "name": data.get("name"),
                "bio": data.get("bio"),
                "avatar_url": data.get("avatar_url"),
                "profile_url": data.get("html_url")
            }
            self._save_to_db(cache_key, profile_data)
            return profile_data
        except Exception:
            return {}

    def get_projects(self, sort_by="stars", limit=10):
        cache_key = "github_projects"
        cached_data = self._get_from_db(cache_key)
        if cached_data:
            return cached_data[:limit]
        url = f"{self.base_url}/users/{self.username}/repos"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            repos = response.json()
            my_repos = [repo for repo in repos if not repo["fork"]]
            if sort_by == "stars":
                my_repos.sort(
                    key=lambda x: x["stargazers_count"], reverse=True)
            projects = [{
                "name": r["name"],
                "description": r["description"] or "No description provided.",
                "language": r["language"] or "Code",
                "stars": r["stargazers_count"],
                "url": r["html_url"],
                "updated_at": datetime.strptime(r["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%b %d, %Y")
            } for r in my_repos]
            self._save_to_db(cache_key, projects)
            return projects[:limit]
        except Exception:
            return []


class LinkedInPortfolio:
    def __init__(self):
        self.username = Config.LINKEDIN_USER
        self.data = get_data_json()
        self.profile = self.data.get("linkedin_profile", {})
        self.experience = self.profile.get("experience", [])
        if "profile_url" not in self.profile:
            self.profile["profile_url"] = f"https://www.linkedin.com/in/{self.username}"

    def get_profile(self): return self.profile
    def get_experience(self): return self.experience


def get_ai_context():
    """Aggregates all dynamic data for the AI system instructions."""
    try:
        gh = GitHubPortfolio()
        li = LinkedInPortfolio()
        knowledge = get_all_knowledge()
        user_profile = get_user_profile()
        db_text = "\n".join(
            [f"{k.category}: {k.info}" for k in knowledge]) if knowledge else "No Database Info."
        repos = gh.get_projects(limit=5)
        repo_text = "\n".join(
            [f"- {r['name']}: {r['description']}" for r in repos]) if repos else "No GitHub Info."
        about_text = li.get_profile().get('about', "Computer Science Student")
        contact_text = f"Email: {user_profile.get('contact_email', 'N/A')}\nGitHub Username: {user_profile.get('github_username', 'N/A')}\nLinkedIn Username: {user_profile.get('linkedin_username', 'N/A')}\nLinkedIn URL: {user_profile.get('linkedin_url', 'N/A')}"
        return f"GITHUB PROJECTS:\n{repo_text}\n\nLINKEDIN PROFILE:\n{about_text}\n\nCONTACT INFO:\n{contact_text}\n\nDATABASE KNOWLEDGE:\n{db_text}"
    except Exception as e:
        logger.error(f"⚠️ Error building context: {e}")
        return "Krishna is a Full Stack Developer."


def seed_initial_data():
    db = SessionLocal()
    data = get_data_json()
    knowledge_list = data.get("knowledge_base", [])
    logger.info("📂 Syncing Knowledge Base...")
    try:
        for entry in knowledge_list:
            existing = db.query(Knowledge).filter_by(
                category=entry['category']).first()
            if existing:
                existing.info = entry['info']
            else:
                db.add(
                    Knowledge(category=entry['category'], info=entry['info']))
        if 'blog_posts' in data:
            db.query(BlogPost).delete()
            for post in data['blog_posts']:
                db.add(BlogPost(
                    title=post['title'], slug=post['slug'], category=post.get(
                        'category', 'Tech'),
                    summary=post['summary'], content=post['content'], image_url=post.get(
                        'image_url'),
                    created_at=datetime.utcnow()
                ))
        if 'projects' in data:
            db.query(Project).delete()
            for proj in data['projects']:
                db.add(Project(
                    title=proj['title'], category=proj.get('category', 'misc'), image_url=proj.get('image_url'),
                    description=proj.get('description'), tech_stack=", ".join(proj.get('tech_stack', [])),
                    github_url=proj.get('github_url'), demo_url=proj.get('demo_url'),
                    is_featured=proj.get('is_featured', False), year=proj.get('year', '')
                ))
        if 'skills' in data:
            db.query(Skill).delete()
            for skill in data['skills']:
                db.add(
                    Skill(category=skill['category'], name=skill['name'], icon_class=skill['icon']))
        if 'services' in data:
            db.query(Service).delete()
            for svc in data['services']:
                db.add(Service(
                    title=svc['title'], description=svc['description'], icon_class=svc['icon']))
        db.query(TimelineEvent).delete()
        if 'academic_timeline' in data:
            for item in data['academic_timeline']:
                db.add(TimelineEvent(
                    type='academic', year=item['year'], title=item['title'],
                    subtitle=item['institution'], description=item['description'],
                    status_badge=item['status'], is_future=False
                ))
        if 'dev_journey' in data:
            for item in data['dev_journey']:
                db.add(TimelineEvent(
                    type='journey', year=item['year'], title=item['title'],
                    subtitle="", description=item['description'],
                    is_future=item.get('is_future', False)
                ))
        db.commit()
        logger.info("✅ DB Sync Completed: All Modules Initialized.")
    except Exception as e:
        logger.error(f"Database Seeding Error: {e}")
        db.rollback()
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    seed_initial_data()
