import os
import logging
import traceback
from flask import Flask
from .config.config import Config
from .db.data import init_db, get_user_profile
from .routes import register_routes
from .errors import errors_bp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .runtime.runtime import PortfolioRuntime
from .diagnostics import DiagnosticEngine
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address, default_limits=[
                  "2000 per day", "500 per hour"], storage_uri="memory://")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    limiter.init_app(app)
    register_routes(app)
    app.register_blueprint(errors_bp)
    with app.app_context():
        from .services.socials import init_github, init_linkedin
        from .assistant.assistant import init_assistant
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
            try:
                print("🚀 Initializing the Systems and Modules")
                logger.info(
                    "🔹 Services: Fetching and Initializing All Components")
                init_db()
                app.assistant = init_assistant()
                app.gh = init_github()
                app.li = init_linkedin()
                if app.assistant:
                    runtime = PortfolioRuntime(app.assistant)
                    runtime.verify_identity()
                    diag = DiagnosticEngine(app)
                    diag.run_route_audit()
                print("All Systems and Modules Initialized Successfully! 🚀")
                print(
                    "Running in Production Mode🚀" if not app.debug else "Running in Development Mode🚀")
            except Exception as e:
                logger.warning(f"❌ Service Initialization Warning: {e}")
                traceback.print_exc()
                app.assistant, app.gh, app.li = None, None, None

    @app.context_processor
    def inject_global_context():
        return {"profile": get_user_profile()}
    return app
