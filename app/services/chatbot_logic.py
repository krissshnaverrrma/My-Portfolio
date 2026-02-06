import logging
from google.genai import types
from .ai_logic import ModelManager
from app.data import get_ai_context, get_ai_config, get_chat_history
logger = logging.getLogger(__name__)


class PortfolioChatBot:
    def __init__(self):
        self.ai_config = get_ai_config()
        self.context_data = get_ai_context()  # Fetched from the unified data source
        self.system_instruction = self._build_system_instruction()
        self.model_manager = ModelManager(
            system_instruction=self.system_instruction)

    def _build_system_instruction(self):
        """Constructs the prompt from JSON template + Dynamic Context."""
        prompt_lines = self.ai_config.get(
            "system_instruction", ["You are an AI assistant."])
        full_prompt = "\n".join(prompt_lines)
        if self.context_data:
            full_prompt += f"\n\nCONTEXT DATA:\n{self.context_data}"
        return full_prompt

    def get_response(self, user_message, session_id="default"):
        raw_history = get_chat_history(session_id)
        formatted_history = []
        for entry in raw_history:
            formatted_history.append(types.Content(
                role="user", parts=[types.Part(text=entry.user_query)]))
            formatted_history.append(types.Content(
                role="model", parts=[types.Part(text=entry.bot_response)]))
        if formatted_history:
            self.model_manager = ModelManager(
                system_instruction=self.system_instruction,
                history=formatted_history
            )
        return self.model_manager.generate_response(user_message, session_id)
