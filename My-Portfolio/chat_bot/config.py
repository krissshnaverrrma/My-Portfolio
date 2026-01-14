import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv(
        "FLASK_SECRET_KEY", "49b61650d550e699479b9e2f6c5b0901a17e0a65c5a45839ecfd54c950d1cc20")
    CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "krishnav24-cs@sanskar.org")
    IS_RENDER = os.getenv("RENDER", "False") == "True"
    if IS_RENDER:
        DATABASE_URL = os.getenv("INTERNAL_DATABASE_URL")
    else:
        DATABASE_URL = os.getenv(
            "EXTERNAL_DATABASE_URL") or "sqlite:///portfolio.db"
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "krissshnaverrrma")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    LINKEDIN_USER = os.getenv("LINKEDIN_USER", "krishna-verma-43aa85315")
