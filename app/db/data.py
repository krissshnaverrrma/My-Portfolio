import logging
import json
from sqlalchemy import inspect, MetaData
from sqlalchemy.sql import func
from types import SimpleNamespace
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from ..config import Config
from .database import SessionLocal, Base, engine
from .models import GeminiCache, GitHubCache, ContactMessage, ChatMessage
from ..utils import load_json_file

logger = logging.getLogger(__name__)

VALID_MODELS_KEY = 'gemini_valid_models'
GLOBAL_CONTEXT_KEY = 'global_portfolio_context_string'
GITHUB_REPOS_KEY = 'github_user_repositories'


class CacheKeys:
    GITHUB_REPOS = GITHUB_REPOS_KEY
    VALID_MODELS = VALID_MODELS_KEY
    GLOBAL_CONTEXT = GLOBAL_CONTEXT_KEY


def load_json_data() -> Dict[str, Any]:
    return load_json_file("app", "db", "data.json")


def _to_obj(data_list: List[Dict]) -> List[SimpleNamespace]:
    return [SimpleNamespace(**item) for item in data_list]


def get_user_profile() -> Dict[str, Any]:
    return load_json_data().get("user_profile", {})


def get_ai_config() -> Dict[str, Any]:
    return load_json_data().get("ai_config", {})


def get_stats() -> Dict[str, Any]:
    return load_json_data().get("stats", {})


def get_core_principles() -> List[Dict]:
    return load_json_data().get("core_principles", [])


def get_core_philosophy() -> List[Dict]:
    return load_json_data().get("core_philosophy", [])


def get_all_skills() -> List[SimpleNamespace]:
    return _to_obj(load_json_data().get("skills", []))


def get_services() -> List[SimpleNamespace]:
    return _to_obj(load_json_data().get("services", []))


def get_interests() -> List[SimpleNamespace]:
    return _to_obj(load_json_data().get("interests", []))


def get_all_projects() -> List[SimpleNamespace]:
    return _to_obj(load_json_data().get("projects", []))


def get_all_posts() -> List[SimpleNamespace]:
    return _to_obj(load_json_data().get("blog_posts", []))


def get_all_certifications() -> List[SimpleNamespace]:
    return _to_obj(load_json_data().get("certifications", []))


def get_timeline(event_type: str) -> List[SimpleNamespace]:
    data = load_json_data()
    if event_type == 'academic':
        return _to_obj(data.get("academic_timeline", []))
    return _to_obj(data.get("dev_journey", []))


def get_all_database() -> List[SimpleNamespace]:
    return _to_obj(load_json_data().get("database", []))


def search_database(user_query: str) -> List[SimpleNamespace]:
    if not user_query or len(user_query) < 3:
        return []
    term = user_query.lower()
    return [
        item for item in get_all_database()
        if term in getattr(item, 'category', '').lower() or term in getattr(item, 'info', '').lower()
    ]


def get_cached_ai_response(cache_key: str, expiry_hours: int = 24) -> Optional[str]:
    with SessionLocal() as db:
        cache_entry = db.query(GeminiCache).filter_by(key=cache_key).first()
        if cache_entry and cache_entry.timestamp:
            current_time = datetime.now(timezone.utc)
            entry_time = cache_entry.timestamp.replace(
                tzinfo=timezone.utc) if cache_entry.timestamp.tzinfo is None else cache_entry.timestamp
            if current_time - entry_time < timedelta(hours=expiry_hours):
                return str(cache_entry.data)
        return None


def set_cached_ai_response(cache_key: str, response_text: str) -> None:
    with SessionLocal() as db:
        try:
            cache_entry = db.query(GeminiCache).filter_by(
                key=cache_key).first()
            if cache_entry:
                cache_entry.data = response_text
                cache_entry.timestamp = func.now()
            else:
                db.add(GeminiCache(key=cache_key, data=response_text))
            db.commit()
        except Exception as e:
            logger.error(f"❌ Gemini Cache Save Failed - {e}")
            db.rollback()


def get_cached_valid_models(expiry_hours: int = 6) -> Optional[List[str]]:
    try:
        with SessionLocal() as db:
            cache_entry = db.query(GeminiCache).filter_by(
                key=VALID_MODELS_KEY).first()
            if cache_entry:
                return json.loads(cache_entry.data)
    except Exception:
        pass
    return None


def set_cached_valid_models(models: List[str]) -> None:
    try:
        with SessionLocal() as db:
            cache_entry = db.query(GeminiCache).filter_by(
                key=VALID_MODELS_KEY).first()
            now_utc = datetime.now(timezone.utc)
            if cache_entry:
                cache_entry.data = json.dumps(models)
                cache_entry.timestamp = now_utc
            else:
                db.add(GeminiCache(key=VALID_MODELS_KEY,
                       data=json.dumps(models), timestamp=now_utc))
            db.commit()
    except Exception as e:
        logger.error(f"❌ DB Cache Write Failed: {e}")


def get_cached_github_data(cache_key: str, expiry_seconds: int = 3600) -> Optional[List[Dict[str, Any]]]:
    try:
        with SessionLocal() as db:
            cache_entry = db.query(GitHubCache).filter_by(
                key=cache_key).first()
            if cache_entry:
                cache_time = cache_entry.timestamp.replace(
                    tzinfo=timezone.utc) if cache_entry.timestamp.tzinfo is None else cache_entry.timestamp
                if (datetime.now(timezone.utc) - cache_time).total_seconds() < expiry_seconds:
                    return json.loads(cache_entry.data)
                else:
                    db.delete(cache_entry)
                    db.commit()
    except Exception:
        pass
    return None


def set_cached_github_data(cache_key: str, data: Any) -> None:
    try:
        with SessionLocal() as db:
            cache_entry = db.query(GitHubCache).filter_by(
                key=cache_key).first()
            if cache_entry:
                cache_entry.data = json.dumps(data)
                cache_entry.timestamp = func.now()
            else:
                db.add(GitHubCache(key=cache_key, data=json.dumps(data)))
            db.commit()
    except Exception as e:
        logger.error(f"❌ GitHub Cache Write Failed - {e}")
        db.rollback()


def save_contact_message(name: str, email: str, subject: str, message: str) -> bool:
    with SessionLocal() as db:
        try:
            subject_text = subject if subject else "No Subject"
            existing_msg = db.query(ContactMessage).filter_by(
                name=name, email=email, subject=subject_text, message=message
            ).first()
            if existing_msg:
                return True
            db.add(ContactMessage(name=name, email=email,
                   subject=subject_text, message=message))
            db.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Contact Message Save Failed - {e}")
            db.rollback()
            return False


def log_conversation(session_id: str, u: str, b: str) -> None:
    if not u or not b:
        return
    with SessionLocal() as db:
        try:
            db.add(ChatMessage(session_id=session_id or "default",
                   user_query=u, bot_response=b))
            db.commit()
        except Exception as e:
            logger.error(f"❌ Chat Log Save Failed - {e}")
            db.rollback()


def get_chat_history(session_id: str, limit: int = 10) -> List[SimpleNamespace]:
    with SessionLocal() as db:
        try:
            logs = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(
                ChatMessage.timestamp.desc()).limit(limit).all()
            return [SimpleNamespace(
                session_id=log.session_id,
                user_query=log.user_query,
                bot_response=log.bot_response,
                timestamp=log.timestamp.isoformat() if log.timestamp else ""
            ) for log in logs][::-1]
        except Exception as e:
            logger.error(f"❌ Error Reading Chat History: {e}")
            return []


def get_database_provider() -> str:
    if getattr(Config, 'IS_RENDER', False):
        return "Internal Database"
    elif not getattr(Config, 'USE_SQLITE_LOCALLY', True):
        return "External Database"
    else:
        return "SQL Database"


def auto_migrate_db():
    Base.metadata.create_all(bind=engine)


def setup_database_tables() -> None:
    provider_name = get_database_provider()
    try:
        auto_migrate_db()
        logger.info(f"✅ Database Initialized via {provider_name}")
    except Exception as e:
        logger.error(f"❌ Database Initialization Failed - {e}")


def init_db() -> None:
    setup_database_tables()
