import os
import json
import logging
import time
import hashlib
from datetime import datetime, timedelta
from google import genai
from google.genai import types
from ..config.config import Config
from ..db.data import (
    log_conversation, search_knowledge, get_ai_config,
    get_chat_history, get_all_knowledge, get_user_profile,
    get_cached_ai_response, set_cached_ai_response,
    get_all_posts, get_all_certifications
)
from ..social.socials import GitHubPortfolio, LinkedInPortfolio

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google.genai").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

_CACHED_MODELS, _LAST_CHECK_TIME, _SHARED_CLIENT = [], None, None
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
    global _SHARED_CLIENT
    if _SHARED_CLIENT is None and Config.GEMINI_API_KEY:
        try:
            _SHARED_CLIENT = genai.Client(api_key=Config.GEMINI_API_KEY)
        except Exception as e:
            logger.error(f"❌ GenAI Client Error: {e}")
    return _SHARED_CLIENT


def get_valid_models():
    global _CACHED_MODELS, _LAST_CHECK_TIME
    if _CACHED_MODELS and _LAST_CHECK_TIME and (datetime.now() - _LAST_CHECK_TIME < _CACHE_EXPIRY):
        return _CACHED_MODELS
    client = get_shared_client()
    if not client:
        return []
    ai_config = get_ai_config()
    json_fallbacks = ai_config.get("fallback_models", [])
    env_preferred = os.getenv("GEMINI_MODEL")
    try:
        api_response = client.models.list()
        available_names = set(m.name.replace("models/", "")
                              for m in api_response)
        valid_stack = []
        if env_preferred and env_preferred in available_names:
            valid_stack.append(env_preferred)
        for model in json_fallbacks:
            if model in available_names and model not in valid_stack:
                valid_stack.append(model)
        if not valid_stack:
            valid_stack = [m for m in available_names if "flash" in m][:2]
        _CACHED_MODELS = valid_stack
        _LAST_CHECK_TIME = datetime.now()
        return valid_stack
    except Exception as e:
        logger.error(f"⚠️ Failed to Fetch Models from GEMINI API: {e}")
        return [env_preferred] + json_fallbacks if env_preferred else json_fallbacks


class AssistantService:
    def __init__(self):
        self.client = get_shared_client()
        self.ai_config = get_ai_config()
        self.model_stack = get_valid_models()
        self.is_online = bool(self.client and self.model_stack)
        self.quick_responses = load_quick_responses()

    def get_masked_key(self):
        key = getattr(Config, 'GEMINI_API_KEY', None)
        if key and len(key) > 8:
            return f"{key[:4]}.."
        return "None/Missing"

    def check_health(self):
        """Self-diagnostic check that now silences internal logs."""
        try:
            res, mode = self.get_response(HEALTH_CHECK_QUERY, silent=True)
            is_healthy = any(w in res.lower()
                             for w in ["assistant", "virtual", "krishna"])
            return is_healthy, mode
        except Exception as e:
            logger.error(f"❌ Assistant Diagnostic Failed: {e}")
            return False, "offline"

    def get_response(self, user_input, session_id="default", silent=False):
        """Modified to support a silent mode for background checks."""
        clean_input = user_input.strip().lower().replace("?", "").replace(".", "")
        if clean_input in self.quick_responses:
            reply = self.quick_responses[clean_input]
            if not silent:
                logger.info(f"🚀 Serving via Quick Response")
            log_conversation(session_id, user_input, reply)
            return reply, "cached_mode"
        instructions = self._build_instructions()
        combined_prompt = f"{instructions}{user_input}"
        cache_key = hashlib.sha256(combined_prompt.encode()).hexdigest()
        cached_reply = get_cached_ai_response(cache_key)
        if cached_reply:
            logger.info("🚀 Serving Response from Smart Cache")
            log_conversation(session_id, user_input, cached_reply)
            return cached_reply, "cached_mode"
        if not self.is_online:
            return self._fallback_search(user_input)
        idx = 0
        history = self._format_history(session_id)
        while idx < len(self.model_stack):
            model_name = self.model_stack[idx]
            try:
                chat = self.client.chats.create(
                    model=model_name,
                    history=history,
                    config=types.GenerateContentConfig(
                        system_instruction=instructions,
                        temperature=0.7
                    )
                )
                response = chat.send_message(user_input)
                reply = response.text.strip()
                if not reply:
                    raise ValueError("Empty Response")
                set_cached_ai_response(cache_key, reply)
                log_conversation(session_id, user_input, reply)
                logger.info(f"🤖 AI Response Generated via : {model_name}")
                return reply, "online"
            except Exception as e:
                next_idx = idx + 1
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    logger.warning(
                        f"🔄 {model_name} Busy (Rate Limit) Exceed. Switching to Next Active Model")
                else:
                    logger.warning(f"⚠️ {model_name} Failed: {str(e)[:50]}")
                if next_idx >= len(self.model_stack):
                    logger.error(
                        "❌ All AI Models Exhausted. Switching to Database Mode")
                    break
                idx = next_idx
                time.sleep(0.3)
        return self._fallback_search(user_input)

    def _get_context(self):
        try:
            gh, li = GitHubPortfolio(), LinkedInPortfolio()
            knowledge = get_all_knowledge()
            user = get_user_profile()
            posts = get_all_posts()
            certs = get_all_certifications()
            repo_text = "\n".join(
                [f"- {r['name']}: {r['description']}" for r in gh.get_projects(limit=5)])
            db_text = "\n".join(
                [f"[{k.category}]: {k.info}" for k in knowledge])
            blog_text = "\n".join(
                [f"- {p.title}: {p.summary}" for p in posts]
            ) if posts else "No Blog Posts Available."
            cert_text = "\n".join(
                [f"- {c.title} by {c.issuer} ({c.status})" for c in certs]
            ) if certs else "No Certifications Listed."
            return (
                f"GITHUB PROJECTS:\n{repo_text}\n\n"
                f"CERTIFICATIONS:\n{cert_text}\n\n"
                f"BLOG POSTS:\n{blog_text}\n\n"
                f"KNOWLEDGE BASE:\n{db_text}\n\n"
                f"CONTACT: {user.get('email', 'N/A')}"
            )
        except Exception as e:
            logger.error(f"Context Build Error: {e}")
            return "Professional Backend Developer Context."

    def _build_instructions(self):
        base = self.ai_config.get("system_instruction", [
                                  "You are an assistant."])
        return "\n".join(base).replace("{context_data}", self._get_context())

    def _format_history(self, session_id):
        raw = get_chat_history(session_id)
        history = []
        for entry in raw:
            history.append(types.Content(role="user", parts=[
                           types.Part(text=entry.user_query)]))
            history.append(types.Content(role="model", parts=[
                           types.Part(text=entry.bot_response)]))
        return history

    def _fallback_search(self, query):
        matches = search_knowledge(query)
        if matches:
            return "\n".join([f"• {m.info}" for m in matches]), "database_mode"
        return "I am Currently Offline.", "offline"
