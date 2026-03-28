import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class AssistantStatus(str, Enum):
    ONLINE = "online"
    CACHED = "cached_mode"
    DATABASE = "database_mode"
    OFFLINE = "offline"
    REFUSED = "refused"


_STYLES = {
    AssistantStatus.ONLINE:   {"color": "\033[92m", "icon": "🤖", "label": "Online Mode"},
    AssistantStatus.CACHED:   {"color": "\033[93m", "icon": "🚀", "label": "Cache Mode"},
    AssistantStatus.DATABASE: {"color": "\033[38;5;214m", "icon": "📂", "label": "Database Mode"},
    AssistantStatus.OFFLINE:  {"color": "\033[91m", "icon": "⚠️", "label": "Offline Mode"},
    AssistantStatus.REFUSED:  {
        "color": "\033[91m", "icon": "🛑", "label": "Refused Mode"}
}

_RESET = "\033[0m"


def log_assistant_response(caller_logger: logging.Logger, status: str, detail: Optional[str] = None) -> None:
    try:
        safe_status = AssistantStatus(status)
    except ValueError:
        safe_status = AssistantStatus.OFFLINE
        detail = f"Unknown Status '{status}' - Defaulting to Offline Mode : {detail}"
    style = _STYLES[safe_status]
    base_msg = f"{style['color']}{style['icon']} [{style['label']}]{_RESET}"
    if detail:
        caller_logger.info(f"{base_msg} - {detail}")
    else:
        caller_logger.info(base_msg)
