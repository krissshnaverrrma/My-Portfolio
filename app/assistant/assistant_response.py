import logging
from enum import Enum
from ..config import Config
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google.genai").setLevel(logging.WARNING)


class AFCRewriter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        if "AFC is enabled" in msg:
            try:
                count = msg.split(":")[-1].strip().replace(".", "")
            except Exception:
                count = "N/A"
                logger.info(
                    f"✅ AI Assistant AFC Function Calling Enabled (Max Parallel Calls: {count})"
                )
            return False
        return True


def apply_dragnet_filter():
    rewriter = AFCRewriter()
    root = logging.getLogger()
    root.addFilter(rewriter)
    for h in root.handlers:
        h.addFilter(rewriter)
    targets = [
        "werkzeug", "flask", "google",
        "google.genai", "urllib3", "httpcore", "httpx"
    ]
    for t in targets:
        l = logging.getLogger(t)
        l.addFilter(rewriter)
        for h in l.handlers:
            h.addFilter(rewriter)
    logger_dict = logging.root.manager.loggerDict
    for name in logger_dict:
        if isinstance(logger_dict[name], logging.Logger):
            logger_dict[name].addFilter(rewriter)
            for h in logger_dict[name].handlers:
                h.addFilter(rewriter)


class AssistantStatus(str, Enum):
    ONLINE = "online"
    CACHED = "cached_mode"
    DATABASE = "database_mode"
    OFFLINE = "offline"


_STYLES = {
    AssistantStatus.ONLINE:   {"color": "\033[92m", "icon": "🤖", "label": "Online Mode"},
    AssistantStatus.CACHED:   {"color": "\033[93m", "icon": "🚀", "label": "Cache Mode"},
    AssistantStatus.DATABASE: {"color": "\033[38;5;214m", "icon": "📂", "label": "Database Mode"},
    AssistantStatus.OFFLINE:  {
        "color": "\033[91m", "icon": "⚠️", "label": "Offline Mode"}
}
_RESET = "\033[0m"


def log_assistant_response(logger: logging.Logger, status: str, detail: str | None = None) -> None:
    try:
        safe_status = AssistantStatus(status)
    except ValueError:
        logger.warning(
            f"Invalid Assistant Status '{status}' Received. Defaulting to OFFLINE.")
        safe_status = AssistantStatus.OFFLINE
    style = _STYLES.get(safe_status, _STYLES[AssistantStatus.OFFLINE])
    color = style.get("color", "")
    icon = style.get("icon", "⚠️")
    label = style.get("label", "UNKNOWN")
    base_msg = f"{icon} AI Assistant Response Initialized on {label}"
    full_msg = f"{base_msg} - {detail}" if detail else base_msg
    logger.info(f"{color}{full_msg}{_RESET}")
