import os
import json
import logging

logger = logging.getLogger(__name__)


def format_postgres_url(url: str) -> str:
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def get_secret_key(env_type: str) -> str:
    key = os.getenv("FLASK_SECRET_KEY")
    if not key:
        raise ValueError(
            f"CRITICAL ERROR: No FLASK_SECRET_KEY Set for {env_type}!")
    return key


def load_json_file(*path_parts) -> dict:
    from ..config.config import Config
    file_path = os.path.join(Config.ROOT_DIR, *path_parts)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            filename = os.path.basename(file_path)
            logger.error(f"⚠️ Error Reading {filename}: {e}")
    return {}
