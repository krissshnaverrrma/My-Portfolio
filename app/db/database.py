import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from ..config.config import get_config
current_config = get_config()
db_url = current_config.DATABASE_URL or "sqlite:///data.db"
engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
    pool_pre_ping=True
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)
db_session = scoped_session(SessionLocal)
Base = declarative_base()


@contextmanager
def get_db():
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise
    finally:
        db_session.remove()
