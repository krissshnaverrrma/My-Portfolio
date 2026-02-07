import os
import sys
import logging
import traceback
from ..db.data import init_db
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy").setLevel(logging.ERROR)


class PortfolioRuntime:
    BOLD, GREEN, RED, BLUE, END = "\033[1m", "\033[92m", "\033[91m", "\033[94m", "\033[0m"

    def __init__(self, bot_instance):
        self.bot = bot_instance

    def verify_identity(self):
        """Essential identity check used by the web app factory."""
        try:
            res, mode = self.bot.get_response("Who are you?")
            is_valid = any(w in res.lower() for w in ["assistant", "virtual"])
            return is_valid, mode
        except:
            return False, "offline"

    def verify_mindset(self):
        """Verifies the mindset instructions are active."""
        try:
            res, _ = self.bot.get_response("What is your coding philosophy?")
            return any(w in res.lower() for w in ["lazy", "efficiency", "automate"])
        except:
            return False

    def run_stress_test(self):
        """Simulates failover logic."""
        stack = self.bot.model_stack
        if len(stack) < 2:
            return "SKIP: Not enough models"
        original_create = self.bot.client.chats.create

        def chaos_mock(*args, **kwargs):
            if kwargs.get('model') == stack[0]:
                raise Exception("429 RESOURCE_EXHAUSTED: Mocked Quota Failure")
            return original_create(*args, **kwargs)
        self.bot.client.chats.create = chaos_mock
        try:
            _, mode = self.bot.get_response("Identify active model.")
            return f"PASS (Switched to {mode})" if "(" + stack[1] + ")" in mode else "FAIL"
        finally:
            self.bot.client.chats.create = original_create


class SystemHealth:
    """Wrapper for diagnostics used by the web route."""

    def __init__(self, bot):
        self.runtime = PortfolioRuntime(bot)
        self.results = {"status": "Initializing", "diagnostics": {}}

    def run_full_diagnostic(self):
        id_ok, mode = self.runtime.verify_identity()
        mind_ok = self.runtime.verify_mindset()
        self.results["diagnostics"].update({
            "role_check": "PASS" if id_ok else "FAIL",
            "mode": mode,
            "mindset_check": "PASS" if mind_ok else "FAIL"
        })
        self.results["status"] = "Healthy" if id_ok and mind_ok else "Degraded"

    def run_stress_test(self):
        self.results["diagnostics"]["stress_test"] = self.runtime.run_stress_test()


if __name__ == "__main__":
    from app.services.chat_bot_service import ChatBotService
    init_db()
    bot = ChatBotService()
    rt = PortfolioRuntime(bot)
    print(f"\n{rt.BOLD}--- Manually CLI Runtime Diagnostics ---{rt.END}")
    id_ok, mode = rt.verify_identity()
    print(f" * Role Check:    {'PASS' if id_ok else 'FAIL'} ({mode})")
    mind_ok = rt.verify_mindset()
    print(f" * Mindset Check: {'PASS' if mind_ok else 'FAIL'}")
    if "--stress" in sys.argv:
        print(f" * Stress Test:   {rt.run_stress_test()}")
