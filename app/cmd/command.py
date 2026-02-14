import os
import sys
import logging
import click
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
        """Registers the 'hub' command to the Flask CLI."""
        @app.cli.command("hub")
        def start_hub():
            """Starts the Centralized System Management Hub."""
            os.environ["FLASK_TESTING"] = "true"
            logging.disable(logging.CRITICAL)
            handler = CLICommandHandler(app)
            print(f"{GREEN}✅ Command Hub Verified.{END}")
            handler.run_interactive_session()

    def verify_commands_at_startup(self):
        """Silently verifies CLI extensions."""
        is_render = self.app.config.get(
            "IS_RENDER", False) if self.app else False
        commands = [c.name for c in self.app.cli.commands.values()]
        if all(cmd in commands for cmd in ["test", "hub"]):
            if not is_render:
                print(
                    f"{GREEN}✅ Command Verified: All CLI Extensions are Registered and Operational{END}")
        else:
            if not is_render:
                print(
                    f"{RED}❌ Command Verified : Critical CLI Extensions Missing.{END}")

    def run_interactive_session(self):
        """Main loop for the interactive management terminal."""
        print(f"\n{BOLD}{CYAN}🌐 SYSTEM CENTRAL HUB (CLI Mode) {END}")
        print(f"{GRAY}commands: ai, db, social, diag, clear, exit{END}")
        while True:
            try:
                cmd_input = input(f"\n{BOLD}{BLUE}hub ~> {END}").strip()
                if not cmd_input:
                    continue
                parts = cmd_input.split(" ", 1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                if cmd in ['exit', 'quit', '0']:
                    print(f"{GRAY}Shutting Down the System{END}")
                    break
                elif cmd == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"{BOLD}{CYAN}🌐 SYSTEM CENTRAL HUB {END}")
                elif cmd == 'help':
                    self._print_help()
                elif cmd == 'ai':
                    self._handle_ai(args if args else cmd_input)
                elif cmd == 'db':
                    self._handle_db()
                elif cmd == 'social':
                    self._handle_social()
                elif cmd == 'diag':
                    self._handle_diag()
                else:
                    self._handle_ai(cmd_input)

            except (EOFError, KeyboardInterrupt):
                break

    def _print_help(self):
        print(f"\n{BOLD}Available Commands:{END}")
        print(
            f"  {CYAN}ai <msg>{END}   : Chat with Assistant (or just type directly)")
        print(f"  {CYAN}db{END}         : View Database Profile Status")
        print(f"  {CYAN}social{END}     : Check GitHub/LinkedIn Integrations")
        print(f"  {CYAN}diag{END}       : Run System Diagnostics (Pytest)")
        print(f"  {CYAN}clear{END}      : Clear terminal screen")
        print(f"  {CYAN}exit{END}       : Exit the hub")

    def _handle_ai(self, message):
        if not message or message == 'ai':
            print(f"{YELLOW}Usage: ai <your message>{END}")
            return
        print(f"{GRAY}Thinking{END}", end="\r")
        try:
            response, mode = current_app.assistant.get_response(message)
            sys.stdout.write("\033[K")
            print(f"{GREEN}AI ({mode}):{END} {response}")
        except Exception as e:
            print(f"{RED}AI Error: {e}{END}")

    def _handle_db(self):
        from app.db.data import get_user_profile
        try:
            profile = get_user_profile()
            if profile:
                print(f"{GREEN}✅ Database Connected.{END}")
                print(f"   User: {BOLD}{profile.get('name', 'N/A')}{END}")
                print(f"   Role: {profile.get('role', 'Developer')}")
            else:
                print(f"{YELLOW}⚠️ Database Connected but Profile is Empty.{END}")
        except Exception as e:
            print(f"{RED}❌ Database Error: {e}{END}")

    def _handle_social(self):
        gh = getattr(current_app, 'gh', None)
        li = getattr(current_app, 'li', None)

        gh_status = f"{GREEN}ONLINE{END}" if gh else f"{RED}OFFLINE{END}"
        li_status = f"{GREEN}ONLINE{END}" if li else f"{RED}OFFLINE{END}"

        print(f"{BOLD}Social Integrations:{END}")
        print(f"   GitHub:   {gh_status}")
        print(f"   LinkedIn: {li_status}")

    def _handle_diag(self):
        from app.test.tests import SystemValidator
        validator = SystemValidator(self.app)
        validator.run_pytest_quietly([])
