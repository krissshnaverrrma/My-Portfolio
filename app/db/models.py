from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100))
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    philosophy: Mapped[str | None] = mapped_column(Text, nullable=True)
    focus: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(
        String(200), nullable=True)
    instagram_url: Mapped[str | None] = mapped_column(
        String(200), nullable=True)
    facebook_url: Mapped[str | None] = mapped_column(
        String(200), nullable=True)
    telegram_url: Mapped[str | None] = mapped_column(
        String(200), nullable=True)
    whatsapp_url: Mapped[str | None] = mapped_column(
        String(200), nullable=True)
    profile_image: Mapped[str | None] = mapped_column(
        String(500), nullable=True)
    profile_icon: Mapped[str | None] = mapped_column(
        String(500), nullable=True)
    bot_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    home_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    home_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    philosophy_title: Mapped[str | None] = mapped_column(
        String(255), nullable=True)
    philosophy_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    projects: Mapped[list["Project"]] = relationship(
        back_populates="author", cascade="all, delete-orphan")
    blog_posts: Mapped[list["BlogPost"]] = relationship(
        back_populates="author", cascade="all, delete-orphan")
    certifications: Mapped[list["Certification"]] = relationship(
        back_populates="author", cascade="all, delete-orphan")


class APICache(Base):
    __tablename__ = 'api_cache'
    key: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    data: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class Knowledge(Base):
    __tablename__ = 'knowledge'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    info: Mapped[str] = mapped_column(Text)


class Skill(Base):
    __tablename__ = 'skills'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    icon_class: Mapped[str] = mapped_column(String(100))


class Service(Base):
    __tablename__ = 'services'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    icon_class: Mapped[str] = mapped_column(String(100))


class TimelineEvent(Base):
    __tablename__ = 'timeline_events'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String(50))
    year: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(200))
    subtitle: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    status_badge: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_future: Mapped[bool] = mapped_column(Boolean, default=False)


class Interest(Base):
    __tablename__ = 'interests'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    icon_class: Mapped[str] = mapped_column(String(100))


class Stat(Base):
    __tablename__ = 'stats'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    projects_completed: Mapped[int] = mapped_column(Integer, default=0)
    certifications: Mapped[int] = mapped_column(Integer, default=0)
    commits_made: Mapped[int] = mapped_column(Integer, default=0)
    cups_of_coffee: Mapped[int] = mapped_column(Integer, default=0)


class CorePrinciple(Base):
    __tablename__ = 'core_principles'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    icon_class: Mapped[str] = mapped_column(String(100))


class CorePhilosophy(Base):
    __tablename__ = 'core_philosophies'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    icon_class: Mapped[str] = mapped_column(String(100))


class ContactMessage(Base):
    __tablename__ = 'contact_messages'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150))
    subject: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class ChatLog(Base):
    __tablename__ = 'chat_logs'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(100), index=True)
    user_query: Mapped[str] = mapped_column(Text)
    bot_response: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class Project(Base):
    __tablename__ = 'projects'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id'), nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(100))
    image_url: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    tech_stack: Mapped[str] = mapped_column(String(255))
    github_url: Mapped[str] = mapped_column(String(500))
    demo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    year: Mapped[str | None] = mapped_column(String(20), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now())
    author: Mapped["User | None"] = relationship(back_populates="projects")


class BlogPost(Base):
    __tablename__ = 'blog_posts'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id'), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(100))
    summary: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str] = mapped_column(String(500))
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now())
    author: Mapped["User | None"] = relationship(back_populates="blog_posts")


class Certification(Base):
    __tablename__ = 'certificates'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id'), nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    issuer: Mapped[str] = mapped_column(String(150))
    date: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    icon_class: Mapped[str] = mapped_column(String(100))
    image_url: Mapped[str] = mapped_column(String(500))
    link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Completed")
    author: Mapped["User | None"] = relationship(
        back_populates="certifications")
