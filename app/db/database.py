import logging
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, Session
from ..config import get_config

logger = logging.getLogger(__name__)

current_config = get_config()


def get_database_url() -> str:
    return getattr(current_config, "SQLALCHEMY_DATABASE_URI", "sqlite:///data.db")


def create_db_engine(url: str):
    is_sqlite = url.startswith("sqlite")
    engine_kwargs = {
        "pool_pre_ping": True,
    }
    if is_sqlite:
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs.update({
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 3600,
        })
    return create_engine(url, **engine_kwargs)


DB_URL = get_database_url()
engine = create_db_engine(DB_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

db_session = scoped_session(SessionLocal)
Base = declarative_base()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    session = db_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database Transaction Failed: {e}")
        raise
    finally:
        session.close()


def init_db_session(app):
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
