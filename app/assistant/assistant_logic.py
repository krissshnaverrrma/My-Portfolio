import os
import json
import logging
from datetime import datetime, timedelta
from google import genai
from ..config.config import Config
from ..db.data import get_ai_config

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google.genai").setLevel(logging.WARNING)
_CACHED_MODELS = []
_LAST_CHECK_TIME = None
_SHARED_CLIENT = None
_CACHE_EXPIRY = timedelta(hours=6)
QUICK_RESPONSE_FILE = 'assistant.json'
HEALTH_CHECK_QUERY = "Who are you?"


def load_quick_responses():
    """Loads the JSON file containing instant answers."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, QUICK_RESPONSE_FILE)
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"⚠️ Failed to Load Quick Responses: {e}")
    return {}


def get_shared_client():
    """Singleton pattern for GenAI Client."""
    global _SHARED_CLIENT
    if _SHARED_CLIENT is None and Config.GEMINI_API_KEY:
        try:
            _SHARED_CLIENT = genai.Client(api_key=Config.GEMINI_API_KEY)
        except Exception as e:
            logger.error(f"❌ GenAI Client Error: {e}")
    return _SHARED_CLIENT


def get_valid_models():
    """
    Fetches and filters available Gemini models.
    Prioritizes environment variable > JSON config > Flash models.
    """
    global _CACHED_MODELS, _LAST_CHECK_TIME
    if _CACHED_MODELS and _LAST_CHECK_TIME:
        if datetime.now() - _LAST_CHECK_TIME < _CACHE_EXPIRY:
            return _CACHED_MODELS
    client = get_shared_client()
    if not client:
        return []
    ai_config = get_ai_config()
    json_fallbacks = ai_config.get("fallback_models", [])
    env_preferred = os.getenv("GEMINI_MODEL")
    valid_stack = []
    try:
        api_response = client.models.list()
        available_names = {m.name.replace("models/", "") for m in api_response}
        if env_preferred and env_preferred in available_names:
            valid_stack.append(env_preferred)
        for model in json_fallbacks:
            if model in available_names and model not in valid_stack:
                valid_stack.append(model)
        if not valid_stack:
            valid_stack = [m for m in available_names if "flash" in m][:2]
        if valid_stack:
            _CACHED_MODELS = valid_stack
            _LAST_CHECK_TIME = datetime.now()
            return valid_stack
    except Exception as e:
        logger.error(f"⚠️ Failed to Fetch Models from GEMINI API: {e}")
    default_stack = [env_preferred] if env_preferred else []
    return default_stack + [m for m in json_fallbacks if m not in default_stack]
