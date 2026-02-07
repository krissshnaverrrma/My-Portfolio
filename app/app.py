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
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address, default_limits=[
                  "200 per day", "50 per hour"], storage_uri="memory://")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    limiter.init_app(app)
    with app.app_context():
        from .db.data import init_db, get_user_profile
        from .services.socials import GitHubPortfolio, LinkedInPortfolio
        from .chat_bot.chat_bot import init_bot
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
            try:
                print("🚀 Initializing the System and Modules")
                logger.info(
                    "🔹 Services: Fetching and Initializing All Components")
                init_db()
                app.bot = init_bot()
                masked_key = app.bot.get_masked_key() if app.bot else "None"
                logger.info(f"✅ AI Connected to GEMINI API Key: {masked_key}")
                runtime = PortfolioRuntime(app.bot)
                valid, mode = runtime.verify_identity()
                if valid:
                    logging.info(f"✅ Identities Verified: ({mode})")
                else:
                    logging.warning(
                        "⚠️ Identities Alert: AI Verification Failed")
                app.gh = GitHubPortfolio()
                app.li = LinkedInPortfolio()
                logger.info(
                    f"✅ AI Initialized on Tier: {getattr(Config, 'GEMINI_MODEL', 'Auto')}")
            except Exception as e:
                logger.warning(f"❌ Service Initialization Warning: {e}")
                traceback.print_exc()
                app.bot, app.gh, app.li = None, None, None
        else:
            app.bot, app.gh, app.li = None, None, None
    register_routes(app)
    app.register_blueprint(errors_bp)

    @app.context_processor
    def inject_global_context():
        return {"profile": get_user_profile()}
    return app
