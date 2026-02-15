import os
import logging
import sys
from flask import Flask
from .config.config import Config
from .db.data import init_db, get_user_profile
from .routes import register_routes
from .errors import errors_bp
from .runtime.runtime import PortfolioRuntime
from .diagnostics import DiagnosticEngine
from .extensions import limiter
from .utils.filters import markdown_filter
from .utils.helpers import format_date
from .test.tests import SystemValidator
from .cmd.command import CLICommandHandler

logger = logging.getLogger(__name__)


def create_app():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    is_cli_mode = os.environ.get(
        "FLASK_CLI_MODE") == "true" or "cli.py" in sys.argv[0]
    quiet_commands = ["test", "hub"]
    is_quiet_mode = any(cmd in sys.argv for cmd in quiet_commands)
    if is_quiet_mode or Config.IS_RENDER:
        os.environ["FLASK_TESTING"] = "true"
        logging.disable(
            logging.WARNING if Config.IS_RENDER else logging.CRITICAL)
        os.environ["WERKZEUG_RUN_MAIN"] = "true"
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        logging.getLogger("flask").setLevel(logging.ERROR)

    app = Flask(__name__)
    app.config.from_object(Config)
    limiter.init_app(app)
    register_routes(app)
    app.register_blueprint(errors_bp)
    app.jinja_env.filters['markdown'] = markdown_filter
    app.jinja_env.filters['format_date'] = format_date
    SystemValidator.register_commands(app)
    CLICommandHandler.register_commands(app)

    with app.app_context():
        from .social.socials import init_github, init_linkedin
        from .assistant.assistant import init_assistant
        is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
        should_init = is_cli_mode or Config.IS_RENDER or is_reloader_process or not app.debug

        if should_init:
            try:
                if app.debug and not Config.IS_RENDER:
                    init_db()
                app.assistant = init_assistant()
                app.gh = init_github()
                app.li = init_linkedin()
                if app.assistant and not is_quiet_mode:
                    runtime = PortfolioRuntime(app.assistant)
                    runtime.verify_identity()
                    diag = DiagnosticEngine(app)
                    diag.run_route_audit()
                    validator = SystemValidator(app)
                    validator.verify_logic_at_startup()
                    cmd_handler = CLICommandHandler(app)
                    cmd_handler.verify_commands_at_startup()
            except Exception as e:
                if not is_quiet_mode:
                    logger.warning(f"Initialization Warning: {e}")
                if not hasattr(app, 'assistant'):
                    app.assistant = None
                if not hasattr(app, 'gh'):
                    app.gh = None
                if not hasattr(app, 'li'):
                    app.li = None
        else:
            app.assistant = None
            app.gh = None
            app.li = None

    @app.context_processor
    def inject_global_context():
        return {"profile": get_user_profile()}

    return app
