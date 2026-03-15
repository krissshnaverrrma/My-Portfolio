import os
import json
import logging
from sqlalchemy import inspect, text, func
from types import SimpleNamespace
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from .database import SessionLocal, Base, engine
from ..config.config import get_config, Config
from .models import (
    User, GeminiCache, GitHubCache, Knowledge, Skill, Service,
    TimelineEvent, Interest, Stat, CorePrinciple, CorePhilosophy,
    ContactMessage, ChatLog, Project, BlogPost, Certification
)

logger = logging.getLogger(__name__)
_JSON_CACHE: Optional[Dict[str, Any]] = None
MODEL_CACHE_KEY = 'gemini_valid_models'


def _get_project_root_path(relative_path: str) -> str:
    root_dir = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root_dir, relative_path)


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


def get_data_json() -> Dict[str, Any]: return load_json_data()
def get_ai_config() -> Dict[str,
                            Any]: return load_json_data().get("ai_config", {})


def get_user_profile(
) -> Dict[str, Any]: return load_json_data().get("user_profile", {})


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
                key=MODEL_CACHE_KEY).first()
            if cache_entry:
                return json.loads(cache_entry.data)
    except Exception as e:
        logger.warning(f"DB Cache Read Failed: {e}")
    return None


def set_cached_valid_models(models: List[str]) -> None:
    try:
        with SessionLocal() as db:
            cache_entry = db.query(GeminiCache).filter_by(
                key=MODEL_CACHE_KEY).first()
            now_utc = datetime.now(timezone.utc)
            if cache_entry:
                cache_entry.data = json.dumps(models)
                cache_entry.timestamp = now_utc
            else:
                db.add(GeminiCache(key=MODEL_CACHE_KEY,
                       data=json.dumps(models), timestamp=now_utc))
            db.commit()
    except Exception as e:
        logger.error(f"DB Cache Write Failed: {e}")


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
    except Exception as e:
        logger.warning(f"DB GitHub Cache Read Failed: {e}")
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


def get_all_knowledge() -> List[Knowledge]:
    with SessionLocal() as db:
        return db.query(Knowledge).order_by(Knowledge.id.asc()).all()


def search_knowledge(user_query: str) -> List[Knowledge]:
    if not user_query or len(user_query) < 3:
        return []
    term = f"%{user_query.lower()}%"
    with SessionLocal() as db:
        return db.query(Knowledge).filter((Knowledge.category.ilike(term)) | (Knowledge.info.ilike(term))).all()


def get_all_skills() -> List[Skill]:
    with SessionLocal() as db:
        return db.query(Skill).order_by(Skill.id.asc()).all()


def get_services() -> List[Service]:
    with SessionLocal() as db:
        return db.query(Service).all()


def get_timeline(event_type: str) -> List[TimelineEvent]:
    with SessionLocal() as db:
        return db.query(TimelineEvent).filter_by(type=event_type).order_by(TimelineEvent.year.desc()).all()


def get_interests() -> List[Interest]:
    with SessionLocal() as db:
        return db.query(Interest).all()


def get_stats() -> Dict[str, Any]: return load_json_data().get("stats", {})


def get_core_principles(
) -> List[CorePrinciple]: return load_json_data().get("core_principles", [])


def get_core_philosophy(
) -> List[Dict[str, Any]]: return load_json_data().get("core_philosophy", [])


def save_contact_message(name, email, subject, message) -> bool:
    with SessionLocal() as db:
        try:
            existing_msg = db.query(ContactMessage).filter_by(
                name=name,
                email=email,
                subject=subject if subject else "No Subject",
                message=message
            ).first()
            if existing_msg:
                logger.info(
                    f"⏭️ Duplicate Message Skipped From {name} ({email})")
                return True
            db.add(ContactMessage(
                name=name,
                email=email,
                subject=subject if subject else "No Subject",
                message=message
            ))
            db.commit()
            logger.info(
                f"📬 New Message Saved for {name} ({email}) | Subject: {subject}")
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
            short_sid = str(session_id)[:8] if session_id else "default"
            short_query = u if len(u) <= 50 else u[:47] + "..."
            existing_log = db.query(ChatLog).filter_by(
                user_query=u,
                bot_response=b
            ).first()
            if existing_log:
                logger.info(
                    f"⏭️ Duplicate Query Skipped : Query: '{short_query}'")
                return
            db.add(ChatLog(
                session_id=session_id or "default",
                user_query=u,
                bot_response=b
            ))
            db.commit()
            logger.info(
                f"💬 New Unique Chat Saved : Session: {short_sid} | Query: '{short_query}'")
        except Exception as e:
            logger.error(f"❌ Chat Log Save Failed - {e}")
            db.rollback()


def get_chat_history(session_id: str, limit: int = 10) -> List[SimpleNamespace]:
    with SessionLocal() as db:
        try:
            logs = db.query(ChatLog).filter(ChatLog.session_id == session_id).order_by(
                ChatLog.timestamp.desc()).limit(limit).all()
            return [SimpleNamespace(session_id=log.session_id, user_query=log.user_query, bot_response=log.bot_response, timestamp=log.timestamp.isoformat() if log.timestamp else "") for log in logs][::-1]
        except Exception as e:
            logger.error(f"❌ Error Reading Chat History: {e}")
            return []


def get_all_projects() -> List[Project]:
    with SessionLocal() as db:
        return db.query(Project).order_by(Project.id.asc()).all()


def get_all_posts() -> List[BlogPost]:
    with SessionLocal() as db:
        return db.query(BlogPost).order_by(BlogPost.id.asc()).all()


def get_all_certifications() -> List[Certification]:
    with SessionLocal() as db:
        return db.query(Certification).order_by(Certification.id.asc()).all()


def seed_initial_data(provider_name: str = "Unknown Provider") -> None:
    db = SessionLocal()
    data = get_data_json()
    try:
        user_prof = data.get("user_profile", {})
        user = db.query(User).filter_by(
            email=user_prof.get("contact_email")).first()
        user_data = {
            "title": user_prof.get("home_title", "Developer"), "name": user_prof.get("name"), "location": user_prof.get("location"),
            "philosophy": user_prof.get("philosophy"), "focus": user_prof.get("focus"), "phone": user_prof.get("contact_phone"),
            "email": user_prof.get("contact_email"), "github_url": f"https://github.com/{user_prof.get('github_username')}",
            "linkedin_url": user_prof.get("linkedin_url"), "instagram_url": user_prof.get("instagram_url"),
            "facebook_url": user_prof.get("facebook_url"), "telegram_url": user_prof.get("telegram_url"),
            "whatsapp_url": user_prof.get("whatsapp_url"), "profile_image": user_prof.get("profile_image"),
            "profile_icon": user_prof.get("profile_icon"), "bot_image": user_prof.get("bot_image"),
            "user_image": user_prof.get("user_image"), "home_title": user_prof.get("home_title"),
            "home_description": user_prof.get("home_description"), "skills_description": user_prof.get("skills_description"),
            "contact_text": user_prof.get("contact_text"), "philosophy_title": user_prof.get("philosophy_title"),
            "philosophy_text": user_prof.get("philosophy_text")
        }
        if not user:
            user = User(**user_data)
            db.add(user)
        else:
            for key, value in user_data.items():
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        current_user_id = user.id

        existing_knowledge = {k.category: k for k in db.query(Knowledge).all()}
        for entry in data.get("knowledge_base", []):
            cat, info = entry['category'], entry['info']
            if cat in existing_knowledge:
                existing_knowledge[cat].info = info
            else:
                db.add(Knowledge(category=cat, info=info))

        if 'skills' in data:
            existing_skills = {s.name: s for s in db.query(Skill).all()}
            for skill in data['skills']:
                icon = skill.get('icon', skill.get('icon_class'))
                if skill['name'] in existing_skills:
                    es = existing_skills[skill['name']]
                    es.category, es.icon_class = skill['category'], icon
                else:
                    db.add(
                        Skill(category=skill['category'], name=skill['name'], icon_class=icon))

        if 'services' in data:
            existing_services = {s.title: s for s in db.query(Service).all()}
            for svc in data['services']:
                icon = svc.get('icon', svc.get('icon_class', 'fas fa-cog'))
                if svc['title'] in existing_services:
                    es = existing_services[svc['title']]
                    es.description, es.icon_class = svc['description'], icon
                else:
                    db.add(
                        Service(title=svc['title'], description=svc['description'], icon_class=icon))

        existing_timelines = {
            (t.title, t.year): t for t in db.query(TimelineEvent).all()}
        for item in data.get('academic_timeline', []):
            key = (item['title'], item['year'])
            if key in existing_timelines:
                et = existing_timelines[key]
                et.subtitle = item.get('institution', "")
                et.description = item.get('description', "")
                et.status_badge = item.get('status', "")
            else:
                db.add(TimelineEvent(type='academic', year=item['year'], title=item['title'], subtitle=item.get(
                    'institution', ""), description=item.get('description', ""), status_badge=item.get('status', ""), is_future=False))

        for item in data.get('dev_journey', []):
            key = (item['title'], item['year'])
            if key in existing_timelines:
                et = existing_timelines[key]
                et.description = item.get('description', "")
                et.is_future = item.get('is_future', False)
                et.subtitle = et.subtitle or ""
                et.status_badge = et.status_badge or ""
            else:
                db.add(TimelineEvent(type='journey', year=item['year'], title=item['title'], subtitle="", description=item.get(
                    'description', ""), status_badge="", is_future=item.get('is_future', False)))

        if 'interests' in data:
            existing_interests = {i.name: i for i in db.query(Interest).all()}
            for item in data['interests']:
                if item['name'] in existing_interests:
                    ei = existing_interests[item['name']]
                    ei.description, ei.icon_class = item['description'], item['icon_class']
                else:
                    db.add(Interest(
                        name=item['name'], description=item['description'], icon_class=item['icon_class']))

        if 'stats' in data:
            s_data = data['stats']
            stat_rec = db.query(Stat).first()
            if not stat_rec:
                stat_rec = Stat()
                db.add(stat_rec)
            stat_rec.projects_completed = s_data.get('projects_completed', 0)
            stat_rec.certifications = s_data.get('certifications', 0)
            stat_rec.commits_made = s_data.get('commits_made', 0)
            stat_rec.cups_of_coffee = s_data.get('cups_of_coffee', 0)

        for section, model in [('core_principles', CorePrinciple), ('core_philosophy', CorePhilosophy)]:
            if section in data:
                existing_items = {i.title: i for i in db.query(model).all()}
                for item in data[section]:
                    if item['title'] in existing_items:
                        ei = existing_items[item['title']]
                        ei.description, ei.icon_class = item['description'], item['icon_class']
                    else:
                        db.add(model(
                            title=item['title'], description=item['description'], icon_class=item['icon_class']))

        if 'projects' in data:
            existing_projects = {p.slug: p for p in db.query(Project).all()}
            for proj in data['projects']:
                slug = proj.get(
                    'slug', proj['title'].lower().replace(' ', '-'))
                proj_fields = {
                    "user_id": current_user_id, "title": proj['title'], "category": proj.get('category', 'misc'),
                    "image_url": proj.get('image_url'), "description": proj.get('description'),
                    "content": proj.get('content', ''), "tech_stack": ", ".join(proj.get('tech_stack', [])),
                    "github_url": proj.get('github_url'), "demo_url": proj.get('demo_url'),
                    "is_featured": proj.get('is_featured', False), "year": proj.get('year', '')
                }
                if slug in existing_projects:
                    for k, v in proj_fields.items():
                        setattr(existing_projects[slug], k, v)
                else:
                    db.add(Project(slug=slug, **proj_fields))

        if 'blog_posts' in data:
            existing_blogs = {b.slug: b for b in db.query(BlogPost).all()}
            for post in data['blog_posts']:
                slug = post.get(
                    'slug', post['title'].lower().replace(' ', '-'))
                blog_fields = {
                    "user_id": current_user_id, "title": post['title'], "category": post.get('category', 'Tech'),
                    "summary": post['summary'], "content": post['content'], "image_url": post.get('image_url'),
                    "is_featured": post.get('is_featured', False)
                }
                if slug in existing_blogs:
                    for k, v in blog_fields.items():
                        setattr(existing_blogs[slug], k, v)
                else:
                    db.add(BlogPost(slug=slug, **blog_fields))

        if 'certifications' in data:
            existing_certs = {c.slug: c for c in db.query(
                Certification).all() if c.slug}
            for cert in data['certifications']:
                slug = cert.get(
                    'slug', cert['title'].lower().replace(' ', '-'))
                cert_fields = {
                    "user_id": current_user_id, "title": cert['title'], "issuer": cert['issuer'],
                    "date": cert.get('date', ''), "description": cert.get('description', ''),
                    "icon_class": cert.get('icon_class', 'fas fa-certificate'),
                    "image_url": cert.get('image_url'), "link": cert.get('link'), "status": cert.get('status', 'Completed')
                }
                if slug in existing_certs:
                    for k, v in cert_fields.items():
                        setattr(existing_certs[slug], k, v)
                else:
                    db.add(Certification(slug=slug, **cert_fields))

        db.commit()
        logger.info(f"✅ Database Initialized - {provider_name}")
    except Exception as e:
        logger.error(f"❌ Database Initialization Failed - {e}")
        db.rollback()
    finally:
        db.close()


def auto_migrate_db():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    expected_tables = Base.metadata.tables.keys()
    tables_to_recreate = set()
    protected_tables = ['chat_logs', 'contact_messages',
                        'gemini_cache', 'github_cache']
    for table_name in expected_tables:
        if table_name in protected_tables and table_name in existing_tables:
            continue
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
            if table_name not in tables_to_recreate and table_name not in protected_tables:
                table_obj = Base.metadata.tables[table_name]
                for fk in table_obj.foreign_keys:
                    if fk.column.table.name in tables_to_recreate:
                        tables_to_recreate.add(table_name)
                        added_new = True
    tables_to_drop = [Base.metadata.tables[t]
                      for t in tables_to_recreate if t in existing_tables]
    if tables_to_drop:
        try:
            Base.metadata.drop_all(bind=engine, tables=tables_to_drop)
        except Exception as e:
            logger.error(f"⚠️ Error Dropping Outdated Tables: {e}")
    tables_to_create = [Base.metadata.tables[t] for t in tables_to_recreate]
    if tables_to_create:
        try:
            Base.metadata.create_all(bind=engine, tables=tables_to_create)
        except Exception as e:
            logger.error(f"⚠️ Error creating new tables: {e}")


def init_db() -> None:
    # 1. THE NUCLEAR WIPE (Remove this block after one successful run!)
    with engine.connect() as conn:
        logger.warning("☢️ STARTING ONE-TIME DATABASE WIPE...")
        # Get all table names manually since we want to kill ghosts too
        inspector = inspect(engine)
        for table in inspector.get_table_names():
            conn.execute(text(f'DROP TABLE "{table}" CASCADE;'))
        conn.commit()
        logger.info("✅ ALL TABLES DROPPED SUCCESSFULLY.")

    # 2. RECREATE & RE-SEED
    # This will now create everything from scratch based on your current models
    Base.metadata.create_all(bind=engine)

    # Identify provider for logs
    provider = "Internal" if Config.IS_RENDER else "External"
    seed_initial_data(provider)

    logger.info(f"🚀 DATABASE RE-INITIALIZED WITH FRESH DATA.")
