import google.generativeai as genai


class ModelManager:
    def __init__(self, system_instruction):
        self.model_stack = ["gemini-2.5-flash",
                            "gemini-2.0-flash-lite", "gemini-1.5-flash"]
        self.current_idx = 0
        self.system_instruction = system_instruction
        self.chat_session = None
        self._initialize_model()

    def _initialize_model(self):
        """Sets Up the Active Model Brain."""
        model_name = self.model_stack[self.current_idx]
        print(f"🧠 Activating Brain: {model_name}")
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=self.system_instruction
        )
        self.chat_session = model.start_chat(history=[])

    def try_fallback(self):
        """Switches to the Next Model if One is Exhausted."""
        if self.current_idx < len(self.model_stack) - 1:
            self.current_idx += 1
            self._initialize_model()
            return True
        return False

    def get_current_name(self):
        return self.model_stack[self.current_idx]
