import os
from contextlib import contextmanager
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from ..config.config import Config

engine = create_engine(
    Config.DATABASE_URL,
    connect_args={
        "check_same_thread": False} if "sqlite" in Config.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def get_db():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class APICache(Base):
    __tablename__ = 'api_cache'
    key = Column(String, primary_key=True, index=True)
    data = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


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


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    slug = Column(String, unique=True, index=True)
    category = Column(String)
    image_url = Column(String)
    description = Column(Text)
    content = Column(Text)
    tech_stack = Column(String)
    github_url = Column(String)
    demo_url = Column(String, nullable=True)
    is_featured = Column(Boolean, default=False)
    year = Column(String, nullable=True)


class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    description = Column(Text)
    icon_class = Column(String)


class TimelineEvent(Base):
    __tablename__ = 'timeline_events'
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    year = Column(String)
    title = Column(String)
    subtitle = Column(String)
    description = Column(Text)
    status_badge = Column(String, nullable=True)
    is_future = Column(Boolean, default=False)


class Service(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    icon_class = Column(String)


class Certification(Base):
    __tablename__ = 'certifications'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    slug = Column(String, unique=True, index=True)
    issuer = Column(String)
    date = Column(String)
    description = Column(Text)
    icon_class = Column(String)
    image_url = Column(String)
    link = Column(String, nullable=True)
    status = Column(String, default="Completed")


class ContactMessage(Base):
    __tablename__ = 'contact_messages'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    subject = Column(String)
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ChatLog(Base):
    __tablename__ = 'chat_logs'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_query = Column(Text)
    bot_response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
