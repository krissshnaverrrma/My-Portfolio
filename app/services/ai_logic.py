import os
import logging
import time
import random
from ..config import Config
from ..data import log_conversation, search_knowledge
from google import genai
from google.genai import types
PREFERRED_ORDER = [
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-2.0-flash-001",
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite"
]


def get_valid_models(client=None):
    """
    Connects to Google to fetch the REAL list of models available.
    """
    valid_models = []
    if not client:
        try:
            if not Config.GEMINI_API_KEY:
                logging.warning("⚠️ No API Key found in Config.")
                return []
            client = genai.Client(api_key=Config.GEMINI_API_KEY)
        except Exception as e:
            logging.error(f"❌ Failed to Create Client for Model Check: {e}")
            return []
    logging.info(
        "📡 Contacting GEMINI AI Studio to Verify Available AI Models...")
    try:
        available_api_models = [m.name.replace(
            "models/", "") for m in client.models.list()]
        for preferred in PREFERRED_ORDER:
            if preferred in available_api_models:
                valid_models.append(preferred)
        if not valid_models:
            logging.warning(
                "⚠️ None of the Preferred Models were Found. Auto-Selecting Available Flash Models.")
            valid_models = [m for m in available_api_models if "flash" in m]
        logging.info(
            f"✅ AI Model Check Completed. Found {len(valid_models)} Usable Models: {valid_models}")
        return valid_models
    except Exception as e:
        logging.error(f"❌ Model Check Failed (API Error): {e}")
        return PREFERRED_ORDER


class ModelManager:
    def __init__(self, system_instruction, history=None):
        self.system_instruction = system_instruction
        self.history = history or []
        self.client = None
        self.chat_session = None
        self.is_online = False
        self.current_idx = 0
        self.model_stack = []
        if self._initialize_client():
            self.model_stack = get_valid_models(self.client)
            self._initialize_model()

    def _initialize_client(self):
        try:
            if Config.GEMINI_API_KEY:
                self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
                return True
            return False
        except Exception as e:
            logging.error(f"AI Client Init Failed: {e}")
            return False

    def _initialize_model(self):
        if not self.model_stack:
            logging.error("❌ No Valid Models Found. Offline Mode.")
            self.is_online = False
            return
        while self.current_idx < len(self.model_stack):
            model_name = self.model_stack[self.current_idx]
            try:
                self.chat_session = self.client.chats.create(
                    model=model_name,
                    history=self.history,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instruction
                    )
                )
                self.is_online = True
                if self.current_idx > 0:
                    logging.info(f"✅ Switched to Model: {model_name}")
                return
            except Exception as e:
                logging.warning(
                    f"⚠️ Init Failed for {model_name}. Skipping...")
                self.current_idx += 1
        logging.error("❌ All AI Models Exhausted. Switching to Offline Mode.")
        self.is_online = False

    def generate_response(self, user_input, session_id="default"):
        while self.is_online and self.current_idx < len(self.model_stack):
            model_name = self.model_stack[self.current_idx]
            try:
                response = self.chat_session.send_message(user_input)
                reply = response.text.strip()
                log_conversation(session_id, user_input, reply)
                return reply, "online"
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    wait_time = random.uniform(2, 5)
                    logging.warning(
                        f"⏳ Rate Limit on {model_name}. Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    try:
                        logging.info(f"🔄 Quick Retry on {model_name}...")
                        response = self.chat_session.send_message(user_input)
                        reply = response.text.strip()
                        log_conversation(session_id, user_input, reply)
                        return reply, "online"
                    except Exception:
                        logging.error(
                            f"❌ Retry failed on {model_name}. Skipping to Next Tier.")
                else:
                    logging.error(f"❌ Error on {model_name}: {e}. Skipping...")
                self.current_idx += 1
                self._initialize_model()
        logging.info(f"📂 Searching Database for: '{user_input}'")
        matches = search_knowledge(user_input)
        if matches:
            logging.info(f"✅ Database Match Found.")
            return "\n".join([f"• {m.info}" for m in matches]), "database_mode"
        logging.warning("⚠️ No Database Match Found. Sending Offline Message.")
        return "I'm Currently Sleeping (System Offline)", "offline_mode"
