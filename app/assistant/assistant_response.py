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
            if not Config.IS_RENDER:
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
    AssistantStatus.ONLINE:   {"color": "\033[92m", "icon": "🤖", "label": "ONLINE"},
    AssistantStatus.CACHED:   {"color": "\033[93m", "icon": "🚀", "label": "CACHE"},
    AssistantStatus.DATABASE: {"color": "\033[38;5;214m", "icon": "📂", "label": "DATABASE"},
    AssistantStatus.OFFLINE:  {
        "color": "\033[91m", "icon": "⚠️", "label": "OFFLINE"}
}
_RESET = "\033[0m"


def log_assistant_response(logger: logging.Logger, status: str, detail: str = None) -> None:
    """Logs the AI Assistant status with a clean, color-coded console output."""
    try:
        safe_status = AssistantStatus(status)
    except ValueError:
        safe_status = AssistantStatus.OFFLINE
    style = _STYLES[safe_status]
    detail_str = f" :: {detail}" if detail else ""
    logger.info(
        f"{style['color']}{style['icon']} [{style['label']}] AI Assistant Response Initialized on Engine{detail_str}{_RESET}"
    )
