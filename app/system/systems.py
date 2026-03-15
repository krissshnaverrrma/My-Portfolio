import os
import sys
import logging
import markdown
import bleach
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ..config.config import get_config, Config
from ..db.data import init_db
from ..social.socials import init_socials
from ..assistant.assistant import init_assistant
logger = logging.getLogger(__name__)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri=os.getenv("REDIS_URL", "memory://")
)


def configure_logging():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    is_cli_mode = os.environ.get(
        "FLASK_CLI_MODE") == "true" or "cli.py" in sys.argv[0]
    quiet_commands = ["test", "hub"]
    is_quiet_mode = any(cmd in sys.argv for cmd in quiet_commands)
    if is_quiet_mode:
        os.environ["FLASK_TESTING"] = "true"
        logging.disable(logging.CRITICAL)
        os.environ["WERKZEUG_RUN_MAIN"] = "true"
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        logging.getLogger("flask").setLevel(logging.ERROR)
    return is_cli_mode, is_quiet_mode


def format_date(value, format='%B %d, %Y'):
    if value:
        return value.strftime(format)
    return ""


def markdown_filter(text: str) -> str:
    if not text:
        return ""
    raw_html = markdown.markdown(
        text, extensions=['fenced_code', 'codehilite'])
    allowed_tags = bleach.sanitizer.ALLOWED_TAGS | {
        'p', 'h1', 'h2', 'h3', 'h4', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'code', 'pre', 'blockquote', 'span'
    }
    allowed_attrs = {
        **bleach.sanitizer.ALLOWED_ATTRIBUTES,
        'a': ['href', 'title', 'target', 'class'],
        'code': ['class'],
        'p': ['class'],
        'h3': ['class'],
        'span': ['class'],
        'pre': ['class']
    }
    return bleach.clean(raw_html, tags=list(allowed_tags), attributes=allowed_attrs)


def initialize_app_services(app: Flask, is_cli_mode: bool, is_quiet_mode: bool) -> None:
    with app.app_context():
        is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
        should_init = is_cli_mode or Config.IS_RENDER or is_reloader_process or not app.debug
        if should_init:
            try:
                logger.info("✅ Initializing the Systems")
                if app.debug or Config.IS_RENDER:
                    init_db()
                app.assistant = init_assistant()
                app.socials = init_socials()
                if not is_quiet_mode:
                    logger.info("✅ System Initialized Successfully")
            except Exception as e:
                if not is_quiet_mode:
                    logger.warning(f"⚠️ System Initialization Warning - {e}")
                app.assistant = getattr(app, 'assistant', None)
                app.socials = getattr(app, 'socials', None)
        else:
            app.assistant = None
            app.socials = None
