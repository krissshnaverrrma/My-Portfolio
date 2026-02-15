import os
import sys
import logging
from contextlib import contextmanager
from flask import current_app
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    from contextlib import contextmanager
    from flask import current_app
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class UI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"

    @staticmethod
    def header(title):
        print(f"\n{UI.BOLD}{UI.BLUE}{title.upper()}{UI.RESET}")
        print(f"{UI.DIM}{'-' * 30}{UI.RESET}")

    @staticmethod
    def item(label, value, color=None):
        c_val = color if color else UI.RESET
        print(f"{UI.DIM} • {UI.RESET}{label:<22} : {c_val}{value}{UI.RESET}")

    @staticmethod
    def success(msg):
        print(f"{UI.GREEN} ✔ {msg}{UI.RESET}")

    @staticmethod
    def error(msg):
        print(f"{UI.RED} ✘ {msg}{UI.RESET}")

    @staticmethod
    def warn(msg):
        print(f"{UI.YELLOW} ⚠ {msg}{UI.RESET}")

    @staticmethod
    def table(headers, rows):
        widths = [len(str(h)) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if len(str(cell)) > widths[i]:
                    widths[i] = len(str(cell))

        widths = [w + 4 for w in widths]
        print("")
        head_str = "".join(
            [f"{UI.BOLD}{h:<{widths[i]}}{UI.RESET}" for i, h in enumerate(headers)])
        print(head_str)
        for row in rows:
            row_str = "".join(
                [f"{str(cell):<{widths[i]}}" for i, cell in enumerate(row)])
            print(f"{UI.DIM}{row_str}{UI.RESET}")
        print("")


@contextmanager
def suppress_startup_logs():
    """Temporarily suppresses stdout/stderr and logging."""
    logger = logging.getLogger()
    previous_level = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)
    original_stdout, original_stderr = sys.stdout, sys.stderr
    with open(os.devnull, "w", encoding="utf-8") as devnull:
        sys.stdout, sys.stderr = devnull, devnull
        try:
            yield
        finally:
            sys.stdout, sys.stderr = original_stdout, original_stderr
            logger.setLevel(previous_level)


def get_app_context():
    with suppress_startup_logs():
        return create_app()


def run_chat():
    """1. Chat with AI"""
    UI.header("Chat with Virtual AI Assistant")
    msg = input(f"{UI.CYAN}Enter Message > {UI.RESET}")
    if not msg:
        return
    print(f"{UI.DIM}AI Thinking{UI.RESET}", end="\r")

    try:
        response, mode = current_app.assistant.get_response(msg)
        sys.stdout.write("\033[K")
        UI.item("Mode", mode, UI.BLUE)
        print(f"\n{response}\n")
    except Exception as e:
        UI.error(f"Error: {e}")


def run_db_seed():
    """Internal Seeding Logic"""
    print(f"\n{UI.YELLOW}WARNING: This will Wipe and Re-Seed All Data.{UI.RESET}")
    if input("Type 'yes' to proceed: ").lower() == 'yes':
        try:
            init_db()
            UI.success("Database Seeded Successfully.")
        except Exception as e:
            UI.error(f"Seeding Failed: {e}")
    else:
        print("Cancelled.")


def run_db_status(target='default'):
    """2. Check Database Status"""
    UI.header("Check Database Status")
    # Lazy imports for models to ensure app context is ready
    from app.db.database import SessionLocal, Project, Skill, BlogPost, Certification, TimelineEvent

    target_map = {'internal': "Internal Data Base",
                  'external': "External Data Base"}
    UI.item("Target", target_map.get(target, "Default Data Base"))

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            UI.item("Connection", "Online", UI.GREEN)

            stats = [
                ["Projects", db.query(Project).count()],
                ["Skills", db.query(Skill).count()],
                ["Blog Posts", db.query(BlogPost).count()],
                ["Certifications", db.query(Certification).count()],
                ["Timeline", db.query(TimelineEvent).count()]
            ]
            UI.table(["Table", "Count"], stats)

            if sum(r[1] for r in stats) == 0:
                UI.warn("Database is Empty.")

            print(f"{UI.DIM}Actions:{UI.RESET}")
            print(" [S] Seed Database  [Enter] Back to Menu")
            if input(f"\n{UI.CYAN}Select > {UI.RESET}").lower() == 's':
                run_db_seed()
    except Exception as e:
        UI.error(f"Connection Failed: {e}")


def run_social_test():
    """3. Social Integrity Check"""
    UI.header("Social Integrity Check")
    gh, li = getattr(current_app, 'gh', None), getattr(current_app, 'li', None)
    UI.item("GitHub Service", "Authenticated" if gh else "Offline",
            UI.GREEN if gh else UI.RED)
    UI.item("LinkedIn Service", "Ready" if li else "Offline",
            UI.GREEN if li else UI.RED)


def run_runtime_test():
    """4. Runtime Verification"""
    UI.header("Runtime Verification")
    from app.runtime.runtime import PortfolioRuntime

    if not current_app.assistant:
        UI.error("Assistant not Initialized. Runtime check Skipped.")
        return

    try:
        runtime = PortfolioRuntime(current_app.assistant)
        with suppress_startup_logs():
            runtime.verify_identity()
        UI.success("Identity Verified: Runtime is Operational")
    except Exception as e:
        UI.error(f"Runtime Check Failed: {e}")


def run_diagnostic_test():
    """5. Diagnostic Verification"""
    UI.header("Diagnostic Verification")
    from app.diagnostics import DiagnosticEngine
    try:
        diag = DiagnosticEngine(current_app)
        with suppress_startup_logs():
            diag.run_route_audit()
        UI.success("Route Verification : All Endpoints Accessible.")
    except Exception as e:
        UI.error(f"Diagnostic Verification Failed: {e}")


def run_unit_tests():
    """6. Tests Verification"""
    UI.header("Tests Verification (Pytest)")
    from app.test.tests import SystemValidator

    print(f"{UI.DIM}Running Test Suite...{UI.RESET}")
    try:
        with suppress_startup_logs():
            validator = SystemValidator(current_app)
            result = validator.run_pytest_quietly([])
    except Exception as e:
        result = -1
        print(f"Test Runner Error: {e}")

    if result == 0:
        UI.success("All Unit Tests Passed.")
    else:
        UI.error("Unit Tests Failed. Check logs for details.")


def run_command_test():
    """7. Command Hub Verification"""
    UI.header("Command Hub Verification")
    from app.cmd.command import CLICommandHandler
    try:
        cmd = CLICommandHandler(current_app)
        with suppress_startup_logs():
            cmd.verify_commands_at_startup()
    except Exception as e:
        UI.error(f"Command Verification Failed: {e}")


def interactive_mode(app):
    first_run = True
    menu_options = {
        '1': run_chat,
        '2': run_db_status,
        '3': run_social_test,
        '4': run_runtime_test,
        '5': run_diagnostic_test,
        '6': run_unit_tests,
        '7': run_command_test
    }

    while True:
        if first_run:
            print(
                f"\n{UI.BOLD}Shutting On the Command Line Interface Mode{UI.RESET}")
            first_run = False
        else:
            print(f"\n{UI.BOLD}CLI MENU{UI.RESET}")

        print("1. Chat with Virtual AI Assistant")
        print("2. Check Database Status")
        print("3. Social Integrity Check")
        print("4. Runtime Verification")
        print("5. Diagnostic Verification")
        print("6. Tests Verification")
        print("7. Command Hub Verification")
        print("0. Exit")

        choice = input(f"\n{UI.CYAN}Select > {UI.RESET}")

        if choice == '0':
            print("Shutting Down the Command Line Interface Mode")
            break

        if choice in menu_options:
            with app.app_context():
                menu_options[choice]()
        else:
            UI.warn("Invalid Selection.")


def main():
    try:
        app = get_app_context()
    except Exception as e:
        print(f"\n{UI.RED}CRITICAL: Failed to Initialize App.{UI.RESET}")
        print(e)
        return
    interactive_mode(app)


if __name__ == "__main__":
    main()
