import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    USE_SQLITE_LOCALLY = os.getenv(
        "USE_SQLITE_LOCALLY", "False").lower() == "true"
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev_key")
    CONTACT_EMAIL = os.getenv("CONTACT_EMAIL")
    IS_RENDER = os.getenv("RENDER", "False").lower() == "true"
    if IS_RENDER:
        DATABASE_URL = os.getenv("INTERNAL_DATABASE_URL")
    elif not USE_SQLITE_LOCALLY:
        DATABASE_URL = os.getenv("EXTERNAL_DATABASE_URL")
    else:
        DATABASE_URL = "sqlite:///portfolio.db"
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    LINKEDIN_USER = os.getenv("LINKEDIN_USER")
