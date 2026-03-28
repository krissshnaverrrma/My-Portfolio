import os
import logging
import markdown
import bleach
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri=os.getenv("REDIS_URL", "memory://")
)


def is_main_process() -> bool:
    return os.environ.get('WERKZEUG_RUN_MAIN') == 'true'


def format_date(value, format_string='%B %d, %Y'):
    if not value:
        return ""
    if isinstance(value, str):
        return value
    try:
        return value.strftime(format_string)
    except AttributeError:
        return str(value)


def markdown_filter(text: str) -> str:
    if not text:
        return ""
    raw_html = markdown.markdown(
        text, extensions=['fenced_code', 'codehilite'])
    allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS | {
        'p', 'h1', 'h2', 'h3', 'h4', 'br', 'strong', 'em', 'ul', 'ol',
        'li', 'a', 'code', 'pre', 'blockquote', 'span'
    })
    allowed_attrs = {
        **bleach.sanitizer.ALLOWED_ATTRIBUTES,
        'a': ['href', 'title', 'target'],
        '*': ['class']
    }
    return bleach.clean(raw_html, tags=allowed_tags, attributes=allowed_attrs)
