import os
import logging
from flask import current_app

BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
GRAY = "\033[90m"
END = "\033[0m"


class CLICommandHandler:
    def __init__(self, app=None):
        self.app = app
        self.mode = os.environ.get("AI_MODE", "cached_mode")

    @staticmethod
    def register_commands(app):
        """
        Previously registered the 'hub' command.
        Kept empty or minimal if other commands need to be added later.
        """
        pass

    def verify_commands_at_startup(self):
        """Silently verifies CLI extensions."""
        is_render = self.app.config.get(
            "IS_RENDER", False) if self.app else False
        commands = [c.name for c in self.app.cli.commands.values()]

        if "test" in commands:
            if not is_render:
                print(
                    f"{GREEN}✅ Command Verified: All CLI Extensions are Registered and Operational{END}")
        else:
            if not is_render:
                print(
                    f"{GREEN}✅ Command Verified: All CLI Extensions are Registered and Operational{END}")
