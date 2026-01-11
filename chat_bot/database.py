import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

INTERNAL_URL = os.getenv("INTERNAL_DATABASE_URL")
EXTERNAL_URL = os.getenv("EXTERNAL_DATABASE_URL")

if os.getenv("RENDER"):
    CURRENT_URL = INTERNAL_URL
    print("🚀 Running on Render at (Internal DB)")
else:
    CURRENT_URL = EXTERNAL_URL or "sqlite:///portfolio.db"
    print(f"💻 Running Locally at (DB: {CURRENT_URL})")

if CURRENT_URL and CURRENT_URL.startswith("postgres://"):
    CURRENT_URL = CURRENT_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in CURRENT_URL else {}
engine = create_engine(CURRENT_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Knowledge(Base):
    __tablename__ = 'knowledge'
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    info = Column(Text)


class ChatLog(Base):
    __tablename__ = 'chat_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_input = Column(Text)
    bot_response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
class BlogPost(Base):
    __tablename__ = 'blog_posts'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)
    content = Column(Text, nullable=False)
    summary = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_all_posts():
    db = SessionLocal()
    try:
        return db.query(BlogPost).order_by(BlogPost.created_at.desc()).all()
    finally:
        db.close()


def get_post_by_slug(slug_text):
    db = SessionLocal()
    try:
        return db.query(BlogPost).filter(BlogPost.slug == slug_text).first()
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database Tables Verified")


def add_fact(category, info):
    if not info:
        return
    db = SessionLocal()
    try:
        new_fact = Knowledge(category=category, info=info)
        db.add(new_fact)
        db.commit()
        print(f"➕ Added: {category}")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


def get_all_knowledge():
    db = SessionLocal()
    try:
        facts = db.query(Knowledge).all()
        if not facts:
            return ""
        text = "\n--- CUSTOM KNOWLEDGE BASE ---\n"
        for fact in facts:
            text += f"- {fact.category}: {fact.info}\n"
        return text
    finally:
        db.close()


def log_conversation(user_text, bot_text):
    db = SessionLocal()
    try:
        log = ChatLog(user_input=user_text, bot_response=bot_text)
        db.add(log)
        db.commit()
    except Exception:
        pass
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    if not db.query(Knowledge).first():
        print("🌱 Seeding Initial Data...")
        add_fact("Contact Email", os.getenv("CONTACT_EMAIL"))
        add_fact("Hobbies", os.getenv("HOBBIES"))
        add_fact("Favorite Technologies", os.getenv("FAVORITE_TECH"))
    else:
        print("✨ Database already has data. Skipping seed.")

    count = db.query(Knowledge).count()
    print(f"📊 Current Fact Count: {count}")
    db.close()
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

INTERNAL_URL = os.getenv("INTERNAL_DATABASE_URL")
EXTERNAL_URL = os.getenv("EXTERNAL_DATABASE_URL")

if os.getenv("RENDER"):
    CURRENT_URL = INTERNAL_URL
    print("🚀 Running on Render at (Internal DB)")
else:
    CURRENT_URL = EXTERNAL_URL or "sqlite:///portfolio.db"
    print(f"💻 Running Locally at (DB: {CURRENT_URL})")

if CURRENT_URL and CURRENT_URL.startswith("postgres://"):
    CURRENT_URL = CURRENT_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in CURRENT_URL else {}
engine = create_engine(CURRENT_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Knowledge(Base):
    __tablename__ = 'knowledge'
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    info = Column(Text)


class ChatLog(Base):
    __tablename__ = 'chat_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_input = Column(Text)
    bot_response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
class BlogPost(Base):
    __tablename__ = 'blog_posts'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)
    content = Column(Text, nullable=False)
    summary = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_all_posts():
    db = SessionLocal()
    try:
        return db.query(BlogPost).order_by(BlogPost.created_at.desc()).all()
    finally:
        db.close()


def get_post_by_slug(slug_text):
    db = SessionLocal()
    try:
        return db.query(BlogPost).filter(BlogPost.slug == slug_text).first()
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database Tables Verified")


def add_fact(category, info):
    if not info:
        return
    db = SessionLocal()
    try:
        new_fact = Knowledge(category=category, info=info)
        db.add(new_fact)
        db.commit()
        print(f"➕ Added: {category}")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


def get_all_knowledge():
    db = SessionLocal()
    try:
        facts = db.query(Knowledge).all()
        if not facts:
            return ""
        text = "\n--- CUSTOM KNOWLEDGE BASE ---\n"
        for fact in facts:
            text += f"- {fact.category}: {fact.info}\n"
        return text
    finally:
        db.close()


def log_conversation(user_text, bot_text):
    db = SessionLocal()
    try:
        log = ChatLog(user_input=user_text, bot_response=bot_text)
        db.add(log)
        db.commit()
    except Exception:
        pass
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    if not db.query(Knowledge).first():
        print("🌱 Seeding Initial Data...")
        add_fact("Contact Email", os.getenv("CONTACT_EMAIL"))
        add_fact("Hobbies", os.getenv("HOBBIES"))
        add_fact("Favorite Technologies", os.getenv("FAVORITE_TECH"))
    else:
        print("✨ Database already has data. Skipping seed.")

    count = db.query(Knowledge).count()
    print(f"📊 Current Fact Count: {count}")
    db.close()
