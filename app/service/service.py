import logging
from flask import Flask
from ..config import Config, get_config
from ..essential import is_main_process
from ..assistant import init_assistant
from ..db import init_db
from ..social import init_socials

logger = logging.getLogger(__name__)


def initialize_app_services(app: Flask) -> None:
    with app.app_context():
        should_init = Config.IS_RENDER or is_main_process() or not app.debug
        if should_init:
            try:
                logger.info("✅ Initializing the Service")
                if app.debug or Config.IS_RENDER:
                    app.database = init_db()
                app.assistant = init_assistant()
                app.socials = init_socials()
                logger.info("✅ Service Initialized Successfully")
            except Exception as e:
                logger.warning(f"⚠️ Service Initialization Warning  {e}")
                app.database = getattr(app, 'database', None)
                app.assistant = getattr(app, 'assistant', None)
                app.socials = getattr(app, 'socials', None)
        else:
            app.database = None
            app.assistant = None
            app.socials = None


def run_server(app):
    active_config = get_config()
    host = active_config.HOST
    port = active_config.PORT
    debug_mode = active_config.DEBUG
    is_render = active_config.IS_RENDER
    if not is_render and is_main_process():
        logger.info(f"✅ Service Running at: http://{host}:{port}")
    app.run(debug=debug_mode, host=host, port=port)
