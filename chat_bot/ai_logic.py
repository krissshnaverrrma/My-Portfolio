import os
import re
import sys

from config import Config
from database import log_conversation, search_knowledge
from google import genai
from google.genai import types


class ModelManager:
    def __init__(self, system_instruction):
        self.system_instruction = system_instruction
        self.client = None
        self.chat_session = None
        self.is_online = False
        if self._initialize_client():
            self.model_stack = self._get_best_available_models()
            self.current_idx = 0
            self._initialize_model()

    def _initialize_client(self):
        try:
            if Config.GEMINI_API_KEY:
                self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
                return True
            return False
        except:
            return False

    def _get_best_available_models(self):
        """
        Asks Google for all available models and ranks them by 'Freshness' and 'Power'.
        Runs silently without printing to console.
        """
        fallback_list = [
            Config.GEMINI_MODEL,
            "gemini-2.5-flash", "gemini-3-flash-preview",
            "gemini-2.0-flash", "gemini-1.5-flash"
        ]
        try:
            all_models = list(self.client.models.list())
            valid_models = []
            for m in all_models:
                name = getattr(m, 'name', '').replace('models/', '')
                if 'gemini' in name and 'embedding' not in name and 'vision' not in name:
                    valid_models.append(name)
            if not valid_models:
                return fallback_list

            def model_scorer(model_name):
                score = 0
                if "gemini-3" in model_name:
                    score += 3000
                elif "gemini-2.5" in model_name:
                    score += 2500
                elif "gemini-2.0" in model_name:
                    score += 2000
                elif "gemini-1.5" in model_name:
                    score += 1500
                if "pro" in model_name:
                    score += 50
                if "flash" in model_name:
                    score += 40
                if "lite" in model_name:
                    score += 20
                if "preview" in model_name or "exp" in model_name:
                    score -= 5
                return score
            valid_models.sort(key=model_scorer, reverse=True)
            final_list = list(dict.fromkeys(valid_models))
            if Config.GEMINI_MODEL in final_list:
                final_list.remove(Config.GEMINI_MODEL)
                final_list.insert(0, Config.GEMINI_MODEL)
            return final_list
        except Exception as e:
            return fallback_list

    def _initialize_model(self):
        if self.current_idx >= len(self.model_stack):
            print("❌ All AI Models Exhausted. Switching to Offline Mode.")
            self.is_online = False
            return
        model_name = self.model_stack[self.current_idx]
        try:
            self.chat_session = self.client.chats.create(
                model=model_name,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction)
            )
            self.is_online = True
            print(f"✅ AI Connected: {model_name}")
        except Exception as e:
            self.current_idx += 1
            self._initialize_model()

    def generate_response(self, user_input):
        if self.is_online and self.chat_session:
            try:
                response = self.chat_session.send_message(user_input)
                reply = response.text.strip()
                log_conversation(user_input, reply)
                return reply, "online"
            except Exception as e:
                self.current_idx += 1
                self._initialize_model()
                if self.is_online:
                    return self.generate_response(user_input)
        matches = search_knowledge(user_input)
        if matches:
            return "\n".join([f"• {m.info}" for m in matches]), "database_mode"
        return "I'm Currently Sleeping (System Offline). Try asking about 'skills' or 'projects'!", "offline_mode"
