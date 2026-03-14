import os
import logging
from ..config.config import get_config
logger = logging.getLogger(__name__)


def run_server(app):
    active_config = get_config()
    host = active_config.HOST
    port = active_config.PORT
    debug_mode = active_config.DEBUG
    is_render = active_config.IS_RENDER
    if not is_render and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        logger.info(f"✅ Service Running at: http://{host}:{port}")
    app.run(debug=debug_mode, host=host, port=port)
