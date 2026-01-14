import os
import sys
from datetime import datetime

from config import Config
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
engine = create_engine(
    Config.DATABASE_URL,
    connect_args={
        "check_same_thread": False} if "sqlite" in Config.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Knowledge(Base):
    __tablename__ = 'knowledge'
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    info = Column(Text)


class BlogPost(Base):
    __tablename__ = 'blog_posts'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    slug = Column(String, unique=True, index=True)
    category = Column(String)
    summary = Column(Text)
    content = Column(Text)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatLog(Base):
    __tablename__ = 'chat_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(Text)
    bot_response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


def get_all_posts():
    """Fetches all blog posts for the /blog route."""
    db = SessionLocal()
    try:
        return db.query(BlogPost).order_by(BlogPost.created_at.desc()).all()
    finally:
        db.close()


def get_all_knowledge():
    """Used by chatbot_logic to load context."""
    db = SessionLocal()
    try:
        return db.query(Knowledge).all()
    finally:
        db.close()


def search_knowledge(query_text):
    """Offline/Database mode search."""
    db = SessionLocal()
    try:
        return db.query(Knowledge).filter(
            (Knowledge.info.ilike(f"%{query_text}%")) |
            (Knowledge.category.ilike(f"%{query_text}%"))
        ).all()
    finally:
        db.close()


def log_conversation(u, b):
    db = SessionLocal()
    try:
        db.add(ChatLog(user_query=u, bot_response=b))
        db.commit()
    finally:
        db.close()


def seed_initial_data():
    """Seeds the database with hardcoded profile data."""
    db = SessionLocal()
    try:
        profile_data = [
            {"category": "hello", "info": "Hi there! The AI is resting, but I'm still here. Ask me about my Projects!"},
            {"category": "hi", "info": "Hey! I'm operating on local database power. What would you like to know?"},
            {"category": "about_me", "info": "Krishna Verma: CS student at SCET with a Lazy Coding mindset—automating tasks for efficiency."},
            {"category": "greeting",
                "info": "Hello! I'm in Database Mode right now (Saving AI quota), but I can still tell you about my Skills, Projects, and Contact info."},
            {"category": "hobbies",
                "info": "Playing Chess, Listening to Music, and Late Night Coding with Lazy Coding Mindset."},
            {"category": "tech_stack", "info": "HTML, CSS, JavaScript, Python, C, C++, Java, SQL, Flask, Django, React, Node.js, Express.js, PostgreSQL, GitHub"},
            {"category": "linkedin",
                "info": f"https://www.linkedin.com/in/{Config.LINKEDIN_USER}"}
        ]
        for entry in profile_data:
            existing = db.query(Knowledge).filter_by(
                category=entry['category']).first()
            if existing:
                existing.info = entry['info']
            else:
                db.add(Knowledge(**entry))
        db.commit()
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    seed_initial_data()


if __name__ == "__main__":
    init_db()
