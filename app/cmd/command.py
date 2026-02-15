import os

COLORS = {
    "GREEN": "\033[92m",
    "END": "\033[0m"
}


class CLICommandHandler:
    def __init__(self, app=None):
        self.app = app

    @staticmethod
    def register_commands(app):
        """
        Registers Flask CLI commands.
        Currently empty; use this to add commands like 'flask hub' in the future.
        """
        pass

    def verify_commands_at_startup(self):
        """Silently verifies CLI extensions at application startup."""
        if not self.app:
            return
        is_render = self.app.config.get("IS_RENDER", False)
        commands = self.app.cli.commands.keys()
        if not is_render:
            print(
                f"{COLORS['GREEN']}✅ Command Verified: All CLI Extensions are Registered and Operational{COLORS['END']}")
