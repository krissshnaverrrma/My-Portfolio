import os
import json
import logging
from sqlalchemy import inspect, text
from types import SimpleNamespace
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from .database import SessionLocal, Base, engine
from ..config.config import get_config, Config
from .models import (
    User, APICache, Knowledge, BlogPost, Project, Skill,
    TimelineEvent, Service, Certification, ContactMessage, ChatLog, Interest, CorePrinciple
)
logger = logging.getLogger(__name__)
_JSON_CACHE: Optional[Dict[str, Any]] = None
CHAT_LOG_FILE = os.path.join('cache', 'assistant_response.json')
CONTACT_MESSAGES_FILE = os.path.join('cache', 'message_response.json')
MODEL_CACHE_FILE = os.path.join('cache', 'model_response.json')
MODEL_CACHE_KEY = 'gemini_valid_models'
GITHUB_CACHE_FILE = os.path.join('cache', 'github_response.json')


def _get_project_root_path(filename: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = os.path.join(base_dir, filename)
    target_dir = os.path.dirname(target_path)
    if target_dir:
        os.makedirs(target_dir, exist_ok=True)
    return target_path


def load_json_data(filename: str = 'data.json') -> Dict[str, Any]:
    global _JSON_CACHE
    if _JSON_CACHE:
        return _JSON_CACHE
    try:
        json_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), filename)
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
    return load_json_data().get("user_profile", {})


def get_ai_config() -> Dict[str, Any]:
    return load_json_data().get("ai_config", {})


def get_all_posts() -> List[BlogPost]:
    with SessionLocal() as db:
        return db.query(BlogPost).order_by(BlogPost.id.asc()).all()


def get_all_projects() -> List[Project]:
    with SessionLocal() as db:
        return db.query(Project).order_by(Project.id.asc()).all()


def get_all_certifications() -> List[Certification]:
    with SessionLocal() as db:
        return db.query(Certification).order_by(Certification.id.asc()).all()


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


def get_interests() -> List[Interest]:
    with SessionLocal() as db:
        return db.query(Interest).all()


def get_core_principles() -> List[CorePrinciple]:
    with SessionLocal() as db:
        return db.query(CorePrinciple).all()


def get_all_knowledge() -> List[Knowledge]:
    with SessionLocal() as db:
        return db.query(Knowledge).order_by(Knowledge.id.asc()).all()


def search_knowledge(user_query: str) -> List[Knowledge]:
    if not user_query or len(user_query) < 3:
        return []
    search_term = f"%{user_query.lower()}%"
    with SessionLocal() as db:
        return db.query(Knowledge).filter(
            (Knowledge.category.ilike(search_term)) |
            (Knowledge.info.ilike(search_term))
        ).all()


def log_conversation(session_id: str, u: str, b: str) -> None:
    timestamp = datetime.now(timezone.utc)
    log_path = _get_project_root_path(CHAT_LOG_FILE)
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
        logger.error(f"❌ Error logging Chat to JSON: {e}")
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
            logger.error(f"❌ Error Logging Chat to Database: {e}")
            db.rollback()


def save_contact_message(name, email, subject, message) -> bool:
    timestamp = datetime.now(timezone.utc)
    log_path = _get_project_root_path(CONTACT_MESSAGES_FILE)
    entry = {
        "timestamp": timestamp.isoformat(),
        "name": name,
        "email": email,
        "subject": subject,
        "message": message
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
        logger.error(f"❌ Error Saving Message to JSON: {e}")
    with SessionLocal() as db:
        try:
            new_msg = ContactMessage(
                name=name, email=email, subject=subject,
                message=message, timestamp=timestamp
            )
            db.add(new_msg)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Error Saving Message to DB: {e}")
            db.rollback()
            return False


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
            logger.error(f"❌ Error Reading Chat History: {e}")
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
                return str(cache_entry.data)
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


def get_cached_valid_models(expiry_hours: int = 6) -> Optional[List[str]]:
    db_models = None
    try:
        with SessionLocal() as db:
            cache_entry = db.query(APICache).filter_by(
                key=MODEL_CACHE_KEY).first()
            if cache_entry:
                cache_time = cache_entry.timestamp
                if cache_time.tzinfo is None:
                    cache_time = cache_time.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) - cache_time < timedelta(hours=expiry_hours):
                    db_models = json.loads(cache_entry.data)
                else:
                    db.delete(cache_entry)
                    db.commit()
    except Exception as e:
        logger.warning(f"DB Cache Read Failed, Falling back to file: {e}")
    if db_models:
        try:
            cache_path = _get_project_root_path(MODEL_CACHE_FILE)
            if not os.path.exists(cache_path):
                with open(cache_path, 'w') as f:
                    json.dump({
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'models': db_models
                    }, f)
        except Exception as e:
            logger.warning(f"File Cache self-healing failed: {e}")
        return db_models
    try:
        cache_path = _get_project_root_path(MODEL_CACHE_FILE)
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if cached_time.tzinfo is None:
                    cached_time = cached_time.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) - cached_time < timedelta(hours=expiry_hours):
                    return cache_data['models']
    except Exception as e:
        logger.warning(f"File Cache Read Failed: {e}")
    return None


def set_cached_valid_models(models: List[str]) -> None:
    try:
        with SessionLocal() as db:
            cache_entry = db.query(APICache).filter_by(
                key=MODEL_CACHE_KEY).first()
            now_utc = datetime.now(timezone.utc)
            if cache_entry:
                cache_entry.data = json.dumps(models)
                cache_entry.timestamp = now_utc
            else:
                new_cache = APICache(
                    key=MODEL_CACHE_KEY,
                    data=json.dumps(models),
                    timestamp=now_utc
                )
                db.add(new_cache)
            db.commit()
    except Exception as e:
        logger.error(f"DB Cache Write Failed: {e}")
    try:
        cache_path = _get_project_root_path(MODEL_CACHE_FILE)
        with open(cache_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'models': models
            }, f)
    except Exception as e:
        logger.error(f"File Cache Write Failed: {e}")


def get_cached_github_data(cache_key: str, expiry_seconds: int = 3600) -> Optional[List[Dict[str, Any]]]:
    db_data = None
    try:
        with SessionLocal() as db:
            cache_entry = db.query(APICache).filter_by(key=cache_key).first()
            if cache_entry:
                cache_time = cache_entry.timestamp
                if cache_time.tzinfo is None:
                    cache_time = cache_time.replace(tzinfo=timezone.utc)
                if (datetime.now(timezone.utc) - cache_time).total_seconds() < expiry_seconds:
                    db_data = json.loads(cache_entry.data)
                else:
                    db.delete(cache_entry)
                    db.commit()
    except Exception as e:
        logger.warning(f"DB GitHub Cache Read Failed: {e}")
    if db_data:
        try:
            cache_path = _get_project_root_path(GITHUB_CACHE_FILE)
            existing_cache = {}
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    existing_cache = json.load(f)
            existing_cache[cache_key] = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': db_data
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(existing_cache, f)
        except Exception as e:
            logger.warning(f"File GitHub Cache Self-Healing Failed: {e}")
        return db_data
    try:
        cache_path = _get_project_root_path(GITHUB_CACHE_FILE)
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            if cache_key in cache_data:
                entry = cache_data[cache_key]
                cached_time = datetime.fromisoformat(entry['timestamp'])
                if cached_time.tzinfo is None:
                    cached_time = cached_time.replace(tzinfo=timezone.utc)
                if (datetime.now(timezone.utc) - cached_time).total_seconds() < expiry_seconds:
                    return entry['data']
    except Exception as e:
        logger.warning(f"File GitHub Cache Read Failed: {e}")
    return None


def set_cached_github_data(cache_key: str, data: Any) -> None:
    now_utc = datetime.now(timezone.utc)
    try:
        with SessionLocal() as db:
            cache_entry = db.query(APICache).filter_by(key=cache_key).first()
            if cache_entry:
                cache_entry.data = json.dumps(data)
                cache_entry.timestamp = now_utc
            else:
                new_cache = APICache(
                    key=cache_key,
                    data=json.dumps(data),
                    timestamp=now_utc
                )
                db.add(new_cache)
            db.commit()
    except Exception as e:
        logger.error(f"DB GitHub Cache Write Failed: {e}")
    try:
        cache_path = _get_project_root_path(GITHUB_CACHE_FILE)
        existing_cache = {}
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                existing_cache = json.load(f)
        existing_cache[cache_key] = {
            'timestamp': now_utc.isoformat(),
            'data': data
        }
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(existing_cache, f, indent=4)
    except Exception as e:
        logger.error(f"File GitHub Cache Write Failed: {e}")


def seed_initial_data(provider_name: str = "Unknown Provider") -> None:
    db = SessionLocal()
    data = get_data_json()
    try:
        user_prof = data.get("user_profile", {})
        user = db.query(User).filter_by(
            email=user_prof.get("contact_email")).first()
        if not user:
            user = User(
                title="Developer",
                name=user_prof.get("name"),
                location=user_prof.get("location"),
                philosophy=user_prof.get("philosophy"),
                focus=user_prof.get("focus"),
                phone=user_prof.get("contact_phone"),
                email=user_prof.get("contact_email"),
                github_url=f"https://github.com/{user_prof.get('github_username')}",
                linkedin_url=user_prof.get("linkedin_url"),
                instagram_url=user_prof.get("instagram_url"),
                facebook_url=user_prof.get("facebook_url"),
                telegram_url=user_prof.get("telegram_url"),
                whatsapp_url=user_prof.get("whatsapp_url"),
                profile_image=user_prof.get("profile_image"),
                profile_icon=user_prof.get("profile_icon"),
                bot_image=user_prof.get("bot_image"),
                user_image=user_prof.get("user_image"),
                home_title=user_prof.get("home_title"),
                home_description=user_prof.get("home_description"),
                philosophy_title=user_prof.get("philosophy_title"),
                philosophy_text=user_prof.get("philosophy_text")
            )
            db.add(user)
        else:
            user.philosophy = user_prof.get("philosophy")
            user.focus = user_prof.get("focus")
            user.phone = user_prof.get("contact_phone")
            user.email = user_prof.get("contact_email")
            user.profile_image = user_prof.get("profile_image")
            user.profile_icon = user_prof.get("profile_icon")
            user.instagram_url = user_prof.get("instagram_url")
            user.facebook_url = user_prof.get("facebook_url")
            user.telegram_url = user_prof.get("telegram_url")
            user.whatsapp_url = user_prof.get("whatsapp_url")
            user.home_title = user_prof.get("home_title")
            user.home_description = user_prof.get("home_description")
            user.philosophy_title = user_prof.get("philosophy_title")
            user.philosophy_text = user_prof.get("philosophy_text")
        db.commit()
        db.refresh(user)
        current_user_id = user.id
        existing_knowledge = {k.category: k for k in db.query(Knowledge).all()}
        knowledge_list = data.get("knowledge_base", [])
        for entry in knowledge_list:
            cat = entry['category']
            info = entry['info']
            if cat in existing_knowledge:
                if existing_knowledge[cat].info != info:
                    existing_knowledge[cat].info = info
            else:
                new_k = Knowledge(category=cat, info=info)
                db.add(new_k)
                existing_knowledge[cat] = new_k
        if 'projects' in data:
            existing_projects = {p.slug: p for p in db.query(Project).all()}
            for proj in data['projects']:
                slug_val = proj.get(
                    'slug', proj['title'].lower().replace(' ', '-'))
                if slug_val not in existing_projects:
                    db.add(Project(
                        user_id=current_user_id, title=proj['title'], slug=slug_val,
                        category=proj.get('category', 'misc'), image_url=proj.get('image_url'),
                        description=proj.get('description'), content=proj.get('content', ''),
                        tech_stack=", ".join(proj.get('tech_stack', [])), github_url=proj.get('github_url'),
                        demo_url=proj.get('demo_url'), is_featured=proj.get('is_featured', False),
                        year=proj.get('year', '')
                    ))
                else:
                    ep = existing_projects[slug_val]
                    ep.title = proj['title']
                    ep.category = proj.get('category', 'misc')
                    ep.image_url = proj.get('image_url')
                    ep.description = proj.get('description')
                    ep.content = proj.get('content', '')
                    ep.tech_stack = ", ".join(proj.get('tech_stack', []))
                    ep.github_url = proj.get('github_url')
                    ep.demo_url = proj.get('demo_url')
                    ep.is_featured = proj.get('is_featured', False)
                    ep.year = proj.get('year', '')
        if 'certifications' in data:
            existing_certs = {c.slug: c for c in db.query(
                Certification).all() if c.slug}
            for cert in data['certifications']:
                slug_val = cert.get(
                    'slug', cert['title'].lower().replace(' ', '-'))
                if slug_val not in existing_certs:
                    db.add(Certification(
                        user_id=current_user_id,
                        title=cert['title'],
                        slug=slug_val,
                        issuer=cert['issuer'],
                        date=cert.get('date', ''),
                        description=cert.get('description', ''),
                        icon_class=cert.get(
                            'icon_class', 'fas fa-certificate'),
                        image_url=cert.get('image_url'),
                        link=cert.get('link'),
                        status=cert.get('status', 'Completed')
                    ))
        if 'blog_posts' in data:
            existing_blogs = {b.slug: b for b in db.query(BlogPost).all()}
            for post in data['blog_posts']:
                slug_val = post.get(
                    'slug', post['title'].lower().replace(' ', '-'))
                if slug_val not in existing_blogs:
                    db.add(BlogPost(
                        user_id=current_user_id, title=post['title'], slug=slug_val,
                        category=post.get('category', 'Tech'), summary=post['summary'],
                        content=post['content'], image_url=post.get(
                            'image_url'),
                        is_featured=post.get('is_featured', False), created_at=datetime.now(timezone.utc)
                    ))
                else:
                    eb = existing_blogs[slug_val]
                    eb.title = post['title']
                    eb.category = post.get('category', 'Tech')
                    eb.summary = post['summary']
                    eb.content = post['content']
                    eb.image_url = post.get('image_url')
                    eb.is_featured = post.get('is_featured', False)
        if 'interests' in data:
            existing_interests = {i.name: i for i in db.query(Interest).all()}
            for int_item in data['interests']:
                if int_item['name'] not in existing_interests:
                    db.add(Interest(
                        name=int_item['name'],
                        description=int_item['description'],
                        icon_class=int_item['icon_class']
                    ))
        if 'core_principles' in data:
            existing_cp = {
                cp.title: cp for cp in db.query(CorePrinciple).all()}
            for cp in data['core_principles']:
                if cp['title'] not in existing_cp:
                    db.add(CorePrinciple(
                        title=cp['title'],
                        description=cp['description'],
                        icon_class=cp['icon_class']
                    ))
        if 'skills' in data:
            existing_skills = {s.slug: s for s in db.query(Skill).all()}
            for skill in data['skills']:
                slug_val = skill.get('slug', skill['name'].lower().replace(
                    ' ', '-').replace('.', '-').replace('/', '').replace('#', 'sharp'))
                if slug_val not in existing_skills:
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
                k_info = f"Skill: {skill['name']} ({skill['category']}). Details: {skill.get('description', '')}"
                if k_category in existing_knowledge:
                    if existing_knowledge[k_category].info != k_info:
                        existing_knowledge[k_category].info = k_info
                else:
                    new_k = Knowledge(category=k_category, info=k_info)
                    db.add(new_k)
                    existing_knowledge[k_category] = new_k
        if 'services' in data:
            existing_services = {s.title: s for s in db.query(Service).all()}
            for svc in data['services']:
                if svc['title'] not in existing_services:
                    db.add(Service(
                        title=svc['title'],
                        description=svc['description'],
                        icon_class=svc.get('icon', svc.get(
                            'icon_class', 'fas fa-cog'))
                    ))
        existing_timelines = {
            (t.title, t.year): t for t in db.query(TimelineEvent).all()}
        if 'academic_timeline' in data:
            for item in data['academic_timeline']:
                if (item['title'], item['year']) not in existing_timelines:
                    db.add(TimelineEvent(
                        type='academic', year=item['year'], title=item['title'],
                        subtitle=item['institution'], description=item['description'],
                        status_badge=item['status'], is_future=False
                    ))
        if 'dev_journey' in data:
            for item in data['dev_journey']:
                if (item['title'], item['year']) not in existing_timelines:
                    db.add(TimelineEvent(
                        type='journey', year=item['year'], title=item['title'],
                        subtitle="", description=item['description'],
                        is_future=item.get('is_future', False)
                    ))
        db.commit()
        if not Config.IS_RENDER:
            logger.info(f"✅ Database Initialized via {provider_name}")
    except Exception as e:
        logger.error(f"Database Seeding Error: {e}")
        db.rollback()
    finally:
        db.close()


def auto_migrate_db():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    expected_tables = Base.metadata.tables.keys()
    tables_to_recreate = set()
    for table_name in expected_tables:
        if table_name not in existing_tables:
            tables_to_recreate.add(table_name)
        else:
            existing_cols = {col['name']
                             for col in inspector.get_columns(table_name)}
            expected_cols = {
                col.name for col in Base.metadata.tables[table_name].columns}
            if existing_cols != expected_cols:
                tables_to_recreate.add(table_name)
    if not tables_to_recreate:
        return
    added_new = True
    while added_new:
        added_new = False
        for table_name in expected_tables:
            if table_name not in tables_to_recreate:
                table_obj = Base.metadata.tables[table_name]
                for fk in table_obj.foreign_keys:
                    if fk.column.table.name in tables_to_recreate:
                        tables_to_recreate.add(table_name)
                        added_new = True
    preserved_data = {
        'chat_logs': [],
        'contact_messages': []
    }
    try:
        with engine.connect() as conn:
            for table in ['chat_logs', 'contact_messages']:
                if table in tables_to_recreate and table in existing_tables:
                    result = conn.execute(text(f"SELECT * FROM {table}"))
                    preserved_data[table] = [
                        dict(row._mapping) for row in result]
    except Exception as e:
        logger.error(f"Error Backing Up Targeted Tables: {e}")
    tables_to_drop = [Base.metadata.tables[t]
                      for t in tables_to_recreate if t in existing_tables]
    Base.metadata.drop_all(bind=engine, tables=tables_to_drop)
    tables_to_create = [Base.metadata.tables[t] for t in tables_to_recreate]
    Base.metadata.create_all(bind=engine, tables=tables_to_create)
    with SessionLocal() as db:
        try:
            if preserved_data['chat_logs']:
                db.bulk_insert_mappings(ChatLog, preserved_data['chat_logs'])
            if preserved_data['contact_messages']:
                db.bulk_insert_mappings(
                    ContactMessage, preserved_data['contact_messages'])
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error Restoring Targeted Table Data: {e}")


def init_db() -> None:
    if Config.IS_RENDER:
        provider = "Internal Database Engine"
    elif not Config.USE_SQLITE_LOCALLY:
        provider = "External Database Engine"
    else:
        provider = "SQL Database Engine"
    auto_migrate_db()
    seed_initial_data(provider)
