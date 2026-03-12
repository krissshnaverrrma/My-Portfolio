import os
import logging
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)


def format_postgres_url(url: str) -> str:
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def get_secret_key(env_type: str) -> str:
    key = os.getenv("FLASK_SECRET_KEY")
    if not key:
        if env_type == "production":
            raise ValueError(
                "CRITICAL ERROR: No FLASK_SECRET_KEY set for Production Environment!")
        logger.warning(
            "FLASK_SECRET_KEY not Found. Using an Insecure Fallback for Development.")
        return "dev-fallback-secret-key-12345"
    return key


class Config:
    CONTACT_EMAIL = os.getenv("CONTACT_EMAIL")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    LINKEDIN_USER = os.getenv("LINKEDIN_USER")
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)
    IS_RENDER = str(os.getenv("RENDER", "False")).lower() == "true"
    USE_SQLITE_LOCALLY = str(
        os.getenv("USE_SQLITE_LOCALLY", "False")).lower() == "true"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT = int(os.environ.get("PORT", os.environ.get("FLASK_RUN_PORT", 5000)))


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = get_secret_key("production")
    DATABASE_URL = format_postgres_url(os.getenv("INTERNAL_DATABASE_URL"))
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    HOST = "0.0.0.0"


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = get_secret_key("development")
    DATABASE_URL = format_postgres_url(os.getenv("EXTERNAL_DATABASE_URL"))
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    HOST = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")


def get_config():
    if os.getenv("APP_ENV") == "production" or Config.IS_RENDER:
        return ProductionConfig
    return DevelopmentConfig
