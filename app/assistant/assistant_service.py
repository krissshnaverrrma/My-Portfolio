import logging
import time
import hashlib
from typing import Tuple, Optional
from .assistant_logic import AssistantCoreLogic, is_query_relevant
from .assistant_response import log_assistant_response
from ..db.data import (
    log_conversation, get_chat_history,
    get_cached_ai_response, set_cached_ai_response,
    search_database
)

logger = logging.getLogger(__name__)


class AssistantService:
    def __init__(self):
        self.logic = AssistantCoreLogic()

    @property
    def status(self) -> str:
        if not getattr(self, 'logic', None):
            return "offline"
        return "online" if getattr(self.logic, 'is_online', False) else "database"

    def get_response(self, user_input: str, session_id: str = "default", silent: bool = False) -> dict:
        clean_input = user_input.strip().lower().replace("?", "").replace(".", "")
        is_duplicate = self._is_duplicate_query(session_id, clean_input)
        if clean_input in self.logic.quick_responses:
            return self._handle_quick_response(
                user_input, clean_input, session_id, is_duplicate, silent
            )
        cache_key = hashlib.sha256(
            f"ai_reply_{session_id}_{clean_input}".encode()).hexdigest()
        cached_reply = get_cached_ai_response(cache_key)
        if cached_reply:
            return self._handle_cached_response(
                user_input, cached_reply, session_id, is_duplicate, silent
            )
        if not is_query_relevant(user_input, self.logic.ai_config):
            if not silent:
                log_assistant_response(logger, "refused", "Refused Query")
            return {"reply": "I cannot Assist with that Request.", "status": "refused"}
        if self.logic.is_online:
            reply, used_model = self._generate_with_retries(
                user_input, session_id)
            if reply:
                set_cached_ai_response(cache_key, reply)
                if not is_duplicate:
                    log_conversation(session_id, user_input, reply)
                if not silent:
                    log_assistant_response(logger, "online", used_model)
                return {"reply": reply, "status": "online"}
        return self._fallback_search(user_input, silent)

    def _is_duplicate_query(self, session_id: str, clean_input: str) -> bool:
        recent_history = get_chat_history(session_id, limit=1)
        return bool(recent_history and recent_history[0].user_query.strip().lower() == clean_input)

    def _handle_quick_response(self, user_input: str, clean_input: str, session_id: str, is_duplicate: bool, silent: bool) -> dict:
        reply = self.logic.quick_responses[clean_input]
        if not silent:
            log_assistant_response(logger, "cached_mode",
                                   "Quick Response")
        if not is_duplicate:
            log_conversation(session_id, user_input, reply)
        return {"reply": reply, "status": "cached_mode"}

    def _handle_cached_response(self, user_input: str, cached_reply: str, session_id: str, is_duplicate: bool, silent: bool) -> dict:
        if not silent:
            log_assistant_response(logger, "cached_mode",
                                   "Cache Response")
        if not is_duplicate:
            log_conversation(session_id, user_input, cached_reply)
        return {"reply": cached_reply, "status": "cached_mode"}

    def _generate_with_retries(self, user_input: str, session_id: str) -> Tuple[Optional[str], Optional[str]]:
        instructions = self.logic.build_instructions()
        history = self.logic.format_history(session_id)
        for model_name in self.logic.model_stack:
            max_retries = 3
            backoff_time = 0.3
            for attempt in range(max_retries):
                try:
                    reply = self.logic.generate_content(
                        model_name, instructions, history, user_input)
                    if reply:
                        return reply, model_name
                    raise ValueError("Empty Response from Model")
                except Exception as e:
                    error_msg = str(e)
                    if ("429" in error_msg or "503" in error_msg or "RESOURCE_EXHAUSTED" in error_msg) and attempt < max_retries - 1:
                        time.sleep(backoff_time)
                        backoff_time *= 2
                    else:
                        break
        return None, None

    def _fallback_search(self, query: str, silent: bool = False) -> dict:
        matches = search_database(query)
        if matches:
            if not silent:
                log_assistant_response(
                    logger, "database_mode", f"Data Base Mode: {len(matches)}")
            return {"reply": "\n".join([f"• {m.info}" for m in matches]), "status": "database_mode"}
        if not silent:
            log_assistant_response(
                logger, "offline", "Offline Mode")
        return {"reply": "System is Currently Offline", "status": "offline"}
