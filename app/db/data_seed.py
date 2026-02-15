import logging
from datetime import datetime, timezone
from .database import (
    SessionLocal, Base, engine, Knowledge, BlogPost,
    Project, Skill, TimelineEvent, Service, Certification
)
from ..config.config import Config
from .data import get_data_json

logger = logging.getLogger(__name__)


def seed_initial_data(provider_name: str = "Unknown Provider") -> None:
    db = SessionLocal()
    data = get_data_json()
    try:
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
                if k_category in existing_knowledge:
                    if existing_knowledge[k_category].info != k_info:
                        existing_knowledge[k_category].info = k_info
                else:
                    new_k = Knowledge(category=k_category, info=k_info)
                    db.add(new_k)
                    existing_knowledge[k_category] = new_k

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
                f"✅ Database Initialized via {provider_name}")
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
