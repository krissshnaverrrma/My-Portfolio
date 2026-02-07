import os
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
    get_cached_ai_response, set_cached_ai_response
)
from ..services.socials import GitHubPortfolio, LinkedInPortfolio

logger = logging.getLogger(__name__)
_CACHED_MODELS, _LAST_CHECK_TIME, _SHARED_CLIENT = [], None, None
_CACHE_EXPIRY = timedelta(hours=6)


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
    env_preferred = os.getenv("GEMINI_MODEL")
    ai_config = get_ai_config()
    json_fallbacks = ai_config.get("fallback_models", [])
    try:
        api_response = client.models.list()
        available_names = [m.name.replace("models/", "") for m in api_response]
        valid_stack = []
        if env_preferred and env_preferred in available_names:
            valid_stack.append(env_preferred)
        for model in json_fallbacks:
            if model in available_names and model not in valid_stack:
                valid_stack.append(model)
        if not valid_stack:
            valid_stack = [m for m in available_names if "flash" in m][:3]
        _CACHED_MODELS = valid_stack
        _LAST_CHECK_TIME = datetime.now()
        return valid_stack
    except Exception:
        return [env_preferred] + json_fallbacks if env_preferred else json_fallbacks


class ChatBotService:
    def __init__(self):
        self.client = get_shared_client()
        self.ai_config = get_ai_config()
        self.model_stack = get_valid_models()
        self.is_online = bool(self.client and self.model_stack)

    def get_masked_key(self):
        """Returns a masked version of the API key for secure logging/display."""
        key = getattr(Config, 'GEMINI_API_KEY', None)
        if key and len(key) > 8:
            return f"{key[:8]}..."
        return "None/Missing"

    def get_response(self, user_input, session_id="default"):
        instructions = self._build_instructions()
        combined_prompt = f"{instructions}{user_input}"
        cache_key = hashlib.sha256(combined_prompt.encode()).hexdigest()
        cached_reply = get_cached_ai_response(cache_key)
        if cached_reply:
            logger.info("🚀 Serving Response from Smart Cache")
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
                        system_instruction=instructions)
                )
                response = chat.send_message(user_input)
                reply = response.text.strip()
                set_cached_ai_response(cache_key, reply)
                log_conversation(session_id, user_input, reply)
                logger.info(f"🤖 AI Response Generated Via: {model_name}")
                return reply, "online"
            except Exception:
                next_idx = idx + 1
                if next_idx < len(self.model_stack):
                    logger.warning(
                        f"🔄 {model_name} Quota Exceeded. Switching to {self.model_stack[next_idx]}...")
                else:
                    logger.warning(
                        f"⚠️ All AI Models Exhausted. Falling Back to Local Database.")
                idx = next_idx
                time.sleep(0.5)
        return self._fallback_search(user_input)

    def _get_context(self):
        try:
            gh, li = GitHubPortfolio(), LinkedInPortfolio()
            knowledge = get_all_knowledge()
            user = get_user_profile()
            repo_text = "\n".join(
                [f"- {r['name']}: {r['description']}" for r in gh.get_projects(limit=5)])
            db_text = "\n".join(
                [f"[{k.category}]: {k.info}" for k in knowledge])
            return f"GITHUB:\n{repo_text}\n\nDB KNOWLEDGE:\n{db_text}\n\nCONTACT: {user.get('email', 'N/A')}"
        except Exception:
            return "Professional Backend Developer context."

    def _build_instructions(self):
        base = self.ai_config.get("system_instruction", [
                                  "You are an assistant."])
        return "\n".join(base).replace("{context_data}", self._get_context())

    def _format_history(self, session_id):
        raw = get_chat_history(session_id)
        return [msg for entry in raw for msg in [
            types.Content(role="user", parts=[
                          types.Part(text=entry.user_query)]),
            types.Content(role="model", parts=[
                          types.Part(text=entry.bot_response)])
        ]]

    def _fallback_search(self, query):
        """Local database search for offline/error states."""
        matches = search_knowledge(query)
        if matches:
            return "\n".join([f"• {m.info}" for m in matches]), "database_mode"
        return "The System is Currently Offline and Unavailable.", "offline"
