import os
import json
import logging
from types import SimpleNamespace
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from .database import (
    SessionLocal, Base, engine, APICache, Knowledge, BlogPost,
    Project, Skill, TimelineEvent, Service, Certification, ContactMessage,
    ChatLog
)
from ..config.config import Config

logger = logging.getLogger(__name__)
_JSON_CACHE: Optional[Dict[str, Any]] = None
CHAT_LOG_FILE = 'chat_logs.json'
CONTACT_MESSAGES_FILE = 'message_response.json'


def load_json_data(filename: str = 'data.json') -> Dict[str, Any]:
    global _JSON_CACHE
    if _JSON_CACHE:
        return _JSON_CACHE
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, filename)
        if not os.path.exists(json_path):
            logger.error(f"❌ File not found: {json_path}")
            return {}
        with open(json_path, 'r', encoding='utf-8') as f:
            _JSON_CACHE = json.load(f)
            return _JSON_CACHE or {}
    except Exception as e:
        logger.error(f"⚠️ Error Loading {filename}: {e}")
        return {}


def get_data_json() -> Dict[str, Any]:
    return load_json_data()


def get_user_profile() -> Dict[str, Any]:
    return get_data_json().get("user_profile", {})


def get_ai_config() -> Dict[str, Any]:
    return get_data_json().get("ai_config", {})


def get_all_posts() -> List[BlogPost]:
    with SessionLocal() as db:
        return db.query(BlogPost).order_by(BlogPost.created_at.desc()).all()


def get_all_projects() -> List[Project]:
    with SessionLocal() as db:
        return db.query(Project).order_by(Project.is_featured.desc(), Project.id.asc()).all()


def get_all_skills() -> List[Skill]:
    with SessionLocal() as db:
        return db.query(Skill).order_by(Skill.id.asc()).all()


def get_skill_by_slug(slug: str) -> Optional[Skill]:
    with SessionLocal() as db:
        return db.query(Skill).filter(Skill.slug == slug).first()


def get_timeline(event_type: str) -> List[TimelineEvent]:
    with SessionLocal() as db:
        return db.query(TimelineEvent).filter_by(type=event_type).order_by(TimelineEvent.year.desc()).all()


def get_services() -> List[Service]:
    with SessionLocal() as db:
        return db.query(Service).all()


def get_all_certifications() -> List[Certification]:
    with SessionLocal() as db:
        return db.query(Certification).order_by(Certification.id.asc()).all()


def get_all_knowledge() -> List[Knowledge]:
    with SessionLocal() as db:
        return db.query(Knowledge).order_by(Knowledge.id.asc()).all()


def search_knowledge(user_query: str) -> List[Knowledge]:
    with SessionLocal() as db:
        all_entries = db.query(Knowledge).all()
        matches = []
        user_query = user_query.lower()
        for entry in all_entries:
            if entry.category.lower() in user_query:
                matches.append(entry)
            elif entry.info and user_query in entry.info.lower() and len(user_query) > 3:
                matches.append(entry)
        return matches


def _get_chat_log_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, CHAT_LOG_FILE)


def log_conversation(session_id: str, u: str, b: str) -> None:
    timestamp = datetime.now(timezone.utc)
    log_path = _get_chat_log_path()
    entry = {
        "session_id": session_id,
        "user_query": u,
        "bot_response": b,
        "timestamp": timestamp.isoformat()
    }
    try:
        data = []
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        data.append(entry)
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"❌ Error logging chat to JSON: {e}")

    with SessionLocal() as db:
        try:
            new_log = ChatLog(
                session_id=session_id,
                user_query=u,
                bot_response=b,
                timestamp=timestamp
            )
            db.add(new_log)
            db.commit()
        except Exception as e:
            logger.error(f"❌ Error logging chat to Database: {e}")
            db.rollback()


def get_chat_history(session_id: str, limit: int = 10) -> List[SimpleNamespace]:
    with SessionLocal() as db:
        try:
            logs = db.query(ChatLog).filter(
                ChatLog.session_id == session_id
            ).order_by(ChatLog.timestamp.desc()).limit(limit).all()
            history_objects = []
            for log in logs:
                history_objects.append(SimpleNamespace(
                    session_id=log.session_id,
                    user_query=log.user_query,
                    bot_response=log.bot_response,
                    timestamp=log.timestamp.isoformat() if log.timestamp else ""
                ))
            return history_objects[::-1]
        except Exception as e:
            logger.error(f"❌ Error Reading Chat Logs from Database: {e}")
            return []


def get_cached_ai_response(cache_key: str, expiry_hours: int = 24) -> Optional[str]:
    with SessionLocal() as db:
        cache_entry = db.query(APICache).filter_by(key=cache_key).first()
        if cache_entry and cache_entry.timestamp:
            current_time = datetime.now(timezone.utc)
            entry_time = cache_entry.timestamp

            if entry_time.tzinfo is None:
                entry_time = entry_time.replace(tzinfo=timezone.utc)

            if current_time - entry_time < timedelta(hours=expiry_hours):
                return cache_entry.data
        return None


def set_cached_ai_response(cache_key: str, response_text: str) -> None:
    with SessionLocal() as db:
        try:
            cache_entry = db.query(APICache).filter_by(key=cache_key).first()
            now_utc = datetime.now(timezone.utc)
            if cache_entry:
                cache_entry.data = response_text
                cache_entry.timestamp = now_utc
            else:
                db.add(APICache(key=cache_key, data=response_text, timestamp=now_utc))
            db.commit()
        except Exception as e:
            logger.error(f"❌ Error Saving to AI Cache: {e}")
            db.rollback()


def _get_contact_log_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, CONTACT_MESSAGES_FILE)


def save_contact_message(name, email, subject, message):
    try:
        log_path = _get_contact_log_path()
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "name": name,
            "email": email,
            "subject": subject,
            "message": message
        }
        data = []
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        data.append(entry)
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"❌ Error Saving Contact Message to JSON: {e}")
    db = SessionLocal()
    try:
        new_msg = ContactMessage(
            name=name, email=email, subject=subject, message=message)
        db.add(new_msg)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"❌ Error Saving Contact Message: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def seed_initial_data(provider_name: str = "Unknown Provider") -> None:
    db = SessionLocal()
    data = get_data_json()
    try:
        knowledge_list = data.get("knowledge_base", [])
        for entry in knowledge_list:
            existing = db.query(Knowledge).filter_by(
                category=entry['category']).first()
            if existing:
                existing.info = entry['info']
            else:
                db.add(
                    Knowledge(category=entry['category'], info=entry['info']))

        if 'projects' in data:
            db.query(Project).delete()
            for proj in data['projects']:
                slug_val = proj.get(
                    'slug', proj['title'].lower().replace(' ', '-'))
                db.add(Project(
                    title=proj['title'],
                    slug=slug_val,
                    category=proj.get('category', 'misc'),
                    image_url=proj.get('image_url'),
                    description=proj.get('description'),
                    content=proj.get('content', ''),
                    tech_stack=", ".join(proj.get('tech_stack', [])),
                    github_url=proj.get('github_url'),
                    demo_url=proj.get('demo_url'),
                    is_featured=proj.get('is_featured', False),
                    year=proj.get('year', '')
                ))

        if 'certifications' in data:
            db.query(Certification).delete()
            for cert in data['certifications']:
                db.add(Certification(
                    title=cert['title'],
                    slug=cert.get('slug'),
                    issuer=cert['issuer'],
                    date=cert.get('date', ''),
                    description=cert.get('description', ''),
                    icon_class=cert.get('icon_class', 'fas fa-certificate'),
                    image_url=cert.get('image_url'),
                    link=cert.get('link'),
                    status=cert.get('status', 'Completed')
                ))

        if 'blog_posts' in data:
            db.query(BlogPost).delete()
            for post in data['blog_posts']:
                db.add(BlogPost(
                    title=post['title'],
                    slug=post['slug'],
                    category=post.get('category', 'Tech'),
                    summary=post['summary'],
                    content=post['content'],
                    image_url=post.get('image_url'),
                    created_at=datetime.now(timezone.utc)
                ))

        if 'skills' in data:
            db.query(Skill).delete()
            for skill in data['skills']:
                slug_val = skill.get('slug', skill['name'].lower().replace(
                    ' ', '-').replace('.', '-').replace('/', '').replace('#', 'sharp'))
                desc_val = skill.get(
                    'description', f"{skill['name']} is a key technology in my {skill['category']} stack.")
                db.add(Skill(
                    category=skill['category'],
                    name=skill['name'],
                    slug=slug_val,
                    description=desc_val,
                    icon_class=skill.get('icon', skill.get('icon_class'))
                ))
                k_category = f"skill_{slug_val}"
                k_info = f"Skill: {skill['name']} ({skill['category']}). Details: {desc_val}"
                existing_k = db.query(Knowledge).filter_by(
                    category=k_category).first()
                if existing_k:
                    existing_k.info = k_info
                else:
                    db.add(Knowledge(category=k_category, info=k_info))

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
        if not Config.IS_RENDER:
            logger.info(
                f"✅ Database Initialized Successfully via {provider_name}")
    except Exception as e:
        logger.error(f"Database Seeding Error: {e}")
        db.rollback()
    finally:
        db.close()


def init_db() -> None:
    if Config.IS_RENDER:
        provider = "Internal Database Engine"
    elif not Config.USE_SQLITE_LOCALLY:
        provider = "External Database Engine"
    else:
        provider = "SQL Database Engine"
    Base.metadata.create_all(bind=engine)
    seed_initial_data(provider)
