import os
from pathlib import Path
from dotenv import load_dotenv
from ..utils import format_postgres_url, get_secret_key

load_dotenv()


def get_bool_env(env_var, default="False"):
    return str(os.getenv(env_var, default)).lower() in ("true", "1", "yes", "t")


class Config:
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
    CONTACT_PHONE = os.getenv("CONTACT_PHONE")
    CONTACT_EMAIL = os.getenv("CONTACT_EMAIL")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))
    IS_RENDER = get_bool_env("RENDER")
    USE_SQLITE_LOCALLY = get_bool_env("USE_SQLITE_LOCALLY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = get_secret_key("production")
    SQLALCHEMY_DATABASE_URI = format_postgres_url(
        os.getenv("INTERNAL_DATABASE_URL"))


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = get_secret_key("development")

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if self.USE_SQLITE_LOCALLY:
            sqlite_path = self.ROOT_DIR / "data.db"
            return f"sqlite:///{sqlite_path}"
        return format_postgres_url(os.getenv("EXTERNAL_DATABASE_URL"))


def get_config():
    env = os.getenv("APP_ENV", "development").lower()
    if Config.IS_RENDER or env == "production":
        return ProductionConfig()
    return DevelopmentConfig()
