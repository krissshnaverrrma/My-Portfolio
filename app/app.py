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
from .utils.logger import configure_logging
from .test.tests import SystemValidator
from .cmd.command import CLICommandHandler

logger = logging.getLogger(__name__)


def create_app():
    is_cli_mode, is_quiet_mode = configure_logging()
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
            if os.environ.get("FLASK_RUN_FROM_CLI") == "true":
                logging.getLogger('app.assistant.assistant').setLevel(
                    logging.WARNING)
                logging.getLogger('app.social.socials').setLevel(
                    logging.WARNING)
                logging.getLogger('app.db.data').setLevel(logging.WARNING)
            try:
                logger.info("✅Initializing All the Systems and Modules")
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
                    logger.info(
                        "✅All the Systems and Modules Initialized Successfully")
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
