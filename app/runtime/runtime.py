import os
import sys
import logging
from ..db.data import get_user_profile, search_knowledge
from ..social.socials import GitHubPortfolio, LinkedInPortfolio


class PortfolioRuntime:
    BOLD, GREEN, RED, BLUE, YELLOW, END = "\033[1m", "\033[92m", "\033[91m", "\033[94m", "\033[93m", "\033[0m"

    def __init__(self, assistant_instance):
        self.assistant = assistant_instance

    def verify_identity(self):
        """Startup Check that now relies on silenced service logic."""
        try:
            ai_ok, mode = self.assistant.check_health()
            db_ok, _ = self.check_database_health()
            kb_ok, _ = self.check_knowledge_redundancy()
            soc_ok, _ = self.check_social_integrations()
            red_ok, _ = self.check_model_redundancy()
            if all([ai_ok, db_ok, kb_ok, soc_ok, red_ok]):
                print(f"{self.GREEN}✅ Runtime Verified: All CONFIGURATION Initialized and Operational (AI: {mode}, Database, Socials, Redundancy){self.END}")
            else:
                print(
                    f"{self.RED}❌ Runtime Verification Failed: Components degraded.{self.END}")
            return ai_ok, mode
        except Exception as e:
            print(f"{self.RED}⚠️ Runtime Critical Error: {e}{self.END}")
            return False, "offline"

    def check_database_health(self):
        try:
            return (True, "connected") if get_user_profile() else (False, "empty")
        except:
            return False, "error"

    def check_knowledge_redundancy(self):
        try:
            results = search_knowledge("project")
            return (True, "active") if results else (True, "empty")
        except:
            return False, "error"

    def check_social_integrations(self):
        try:
            GitHubPortfolio()
            LinkedInPortfolio()
            return True, "active"
        except:
            return False, "failure"

    def check_model_redundancy(self):
        count = len(self.assistant.model_stack)
        return (count > 1), f"{count}_models"
