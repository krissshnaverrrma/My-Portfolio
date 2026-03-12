import os
import json
import logging
from google import genai
from ..config.config import Config
from ..db.data import get_ai_config, get_cached_valid_models, set_cached_valid_models
logger = logging.getLogger(__name__)
_SHARED_CLIENT = None
QUICK_RESPONSE_FILE = 'assistant.json'
HEALTH_CHECK_QUERY = "Who are you?"


def load_quick_responses():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, QUICK_RESPONSE_FILE)
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                cleaned_data = {}
                for key, value in raw_data.items():
                    clean_key = key.strip().lower().replace("?", "").replace(".", "")
                    cleaned_data[clean_key] = value
                return cleaned_data
    except Exception as e:
        logger.error(f"⚠️ Failed to Load Quick Responses: {e}")
    return {}


def get_shared_client():
    global _SHARED_CLIENT
    if _SHARED_CLIENT is None and Config.GEMINI_API_KEY:
        try:
            _SHARED_CLIENT = genai.Client(api_key=Config.GEMINI_API_KEY)
        except Exception as e:
            logger.error(f"❌ GenAI Client Initialization Error: {e}")
    return _SHARED_CLIENT


def get_valid_models():
    cached_models = get_cached_valid_models()
    if cached_models:
        return cached_models
    client = get_shared_client()
    ai_config = get_ai_config()
    json_fallbacks = ai_config.get("fallback_models", [])
    env_preferred = os.getenv("GEMINI_MODEL")
    if not client:
        logger.warning(
            "No GenAI Client Available. Relying Strictly on Fallbacks.")
        default_stack = [env_preferred] if env_preferred else []
        return default_stack + [m for m in json_fallbacks if m not in default_stack]
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
            set_cached_valid_models(valid_stack)
            return valid_stack
    except Exception as e:
        logger.error(f"⚠️ Failed to Fetch Models from GEMINI API: {e}")
    default_stack = [env_preferred] if env_preferred else []
    return default_stack + [m for m in json_fallbacks if m not in default_stack]
