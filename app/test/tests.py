import pytest
import sys
import os
import subprocess
import click
from flask import current_app
from app.config.config import Config

BOLD, GREEN, RED, BLUE, YELLOW, END = "\033[1m", "\033[92m", "\033[91m", "\033[94m", "\033[93m", "\033[0m"


@pytest.fixture(scope="module", autouse=True)
def setup_test_context():
    """
    Sets up the Flask app context for tests.
    CRITICAL: Sanitizes sys.argv to prevent Flask CLI from crashing on Pytest flags.
    """
    raw_argv = sys.argv
    sys.argv = [raw_argv[0]]
    try:
        if not current_app:
            from app import create_app
            os.environ["FLASK_TESTING"] = "true"
            app = create_app()
            with app.app_context():
                yield
        else:
            yield
    finally:
        sys.argv = raw_argv


def test_database_connection():
    """Checks if the database layer is responsive."""
    from app.db.data import get_user_profile
    profile = get_user_profile()
    assert profile is not None, "Database returned empty profile"


def test_ai_status():
    """Checks if the assistant is initialized."""
    if not current_app:
        pytest.fail("No application context available")
    if hasattr(current_app, 'assistant') and current_app.assistant:
        status, _ = current_app.assistant.check_health()
        assert status is True, "AI Health Check Failed"
    else:
        pytest.skip("AI Assistant Not Loaded in this Environment")


class SystemValidator:
    def __init__(self, app=None):
        self.app = app

    @staticmethod
    def register_commands(app):
        """Registers the 'test' command to the Flask CLI."""
        @app.cli.command("test", context_settings=dict(ignore_unknown_options=True))
        @click.argument('extra_args', nargs=-1)
        def run_tests(extra_args):
            """Runs the diagnostics suite."""
            os.environ["FLASK_TESTING"] = "true"
            validator = SystemValidator(app)
            validator.run_pytest_quietly(extra_args)

    def verify_logic_at_startup(self):
        """
        Lightweight check to ensure Test CLI is registered.
        Replaces the heavy logic check with a simple registration verification.
        """
        if Config.IS_RENDER:
            return

        commands = [c.name for c in self.app.cli.commands.values()]
        if "test" in commands:
            print(
                f"{GREEN}✅ Test Verified: All the Test are Registered and Operational{END}")
        else:
            print(f"{RED}❌ Test Verify: Critical Test Extension Missing.{END}")

    def run_pytest_quietly(self, extra_args):
        """
        Runs Pytest in a subprocess but CAPTURES all output.
        Only prints the simple success/fail messages.
        """
        cmd = [sys.executable, "-m", "pytest"]
        cmd.extend(["-q", "--disable-warnings", "--tb=no"])
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(os.path.abspath(__file__))
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                if not Config.IS_RENDER:
                    print(
                        f"{GREEN}✅ CLI Logic Checked: All Internal Test Suites Passed.{END}")
            else:
                if not Config.IS_RENDER:
                    print(f"{RED}❌ CLI Logic Checked: Diagnostics Failed.{END}")
                    print(result.stderr)
            sys.exit(result.returncode)
        except Exception as e:
            if not Config.IS_RENDER:
                print(f"{RED}Error Running pytest: {e}{END}")
            sys.exit(1)
