import logging
from ..config import Config
from .assistant_logic import apply_dragnet_filter
from .assistant_service import AssistantService

logger = logging.getLogger(__name__)


def get_assistant_provider() -> str:
    return getattr(Config, 'GEMINI_MODEL', 'Auto')


def setup_assistant_service():
    provider_name = get_assistant_provider()
    try:
        apply_dragnet_filter()
        assistant = AssistantService()
        if assistant and getattr(assistant, 'logic', None) and assistant.logic.is_online:
            logger.info(f"✅ AI Assistant Initialized via {provider_name}")
        else:
            logger.warning("⚠️ AI Assistant Initialized via OFFLINE Mode")
        return assistant
    except Exception as e:
        logger.error(f"❌ AI Assistant Initialization Failed - {e}")
        return None


def init_assistant():
    return setup_assistant_service()
