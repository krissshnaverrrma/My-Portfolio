
import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from .database import (
    SessionLocal, Base, engine, APICache, Knowledge, BlogPost,
    Project, Skill, TimelineEvent, Service, ChatLog, Certification, ContactMessage
)

logger = logging.getLogger(__name__)
_JSON_CACHE: Optional[Dict[str, Any]] = None


def load_json_data(filename: str = 'data.json') -> Dict[str, Any]:
    """Loads data from the JSON file located in the parent directory (app/)."""
    global _JSON_CACHE
    if _JSON_CACHE:
        return _JSON_CACHE
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
        return db.query(Skill).all()


def get_timeline(event_type: str) -> List[TimelineEvent]:
    with SessionLocal() as db:
        return db.query(TimelineEvent).filter_by(type=event_type).all()


def get_services() -> List[Service]:
    with SessionLocal() as db:
        return db.query(Service).all()


def get_all_certifications() -> List[Certification]:
    with SessionLocal() as db:
        return db.query(Certification).all()


def get_all_knowledge() -> List[Knowledge]:
    with SessionLocal() as db:
        return db.query(Knowledge).all()


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


def log_conversation(session_id: str, u: str, b: str) -> None:
    with SessionLocal() as db:
        db.add(ChatLog(session_id=session_id, user_query=u, bot_response=b))
        db.commit()


def get_chat_history(session_id: str, limit: int = 10) -> List[ChatLog]:
    with SessionLocal() as db:
        return db.query(ChatLog).filter_by(session_id=session_id)\
                 .order_by(ChatLog.timestamp.desc()).limit(limit).all()[::-1]


def get_cached_ai_response(cache_key: str, expiry_hours: int = 24) -> Optional[str]:
    """Retrieves a response from the cache if it hasn't expired."""
    with SessionLocal() as db:
        cache_entry = db.query(APICache).filter_by(key=cache_key).first()
        if cache_entry:
            if datetime.utcnow() - cache_entry.timestamp < timedelta(hours=expiry_hours):
                return cache_entry.data
        return None


def set_cached_ai_response(cache_key: str, response_text: str) -> None:
    """Saves or updates an AI response in the database cache."""
    with SessionLocal() as db:
        try:
            cache_entry = db.query(APICache).filter_by(key=cache_key).first()
            if cache_entry:
                cache_entry.data = response_text
                cache_entry.timestamp = datetime.utcnow()
            else:
                db.add(APICache(key=cache_key, data=response_text))
            db.commit()
        except Exception as e:
            logger.error(f"❌ Error saving to AI Cache: {e}")
            db.rollback()


def save_contact_message(name, email, subject, message):
    db = SessionLocal()
    try:
        new_msg = ContactMessage(
            name=name, email=email, subject=subject, message=message)
        db.add(new_msg)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"❌ Error saving contact message: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def seed_initial_data() -> None:
    db = SessionLocal()
    data = get_data_json()
    logger.info("📂 Syncing Knowledge Base and Initial Data")
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
                    created_at=datetime.utcnow()
                ))

        if 'projects' in data:
            db.query(Project).delete()
            for proj in data['projects']:
                db.add(Project(
                    title=proj['title'],
                    category=proj.get('category', 'misc'),
                    image_url=proj.get('image_url'),
                    description=proj.get('description'),
                    tech_stack=", ".join(proj.get('tech_stack', [])),
                    github_url=proj.get('github_url'),
                    demo_url=proj.get('demo_url'),
                    is_featured=proj.get('is_featured', False),
                    year=proj.get('year', '')
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

        if 'certifications' in data:
            db.query(Certification).delete()
            for cert in data['certifications']:
                db.add(Certification(
                    title=cert['title'],
                    issuer=cert['issuer'],
                    date=cert.get('date', ''),
                    description=cert.get('description', ''),
                    icon_class=cert.get('icon', 'fas fa-certificate'),
                    link=cert.get('link'),
                    status=cert.get('status', 'Completed')
                ))

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


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    seed_initial_data()
