import logging
from .assistant_service import AssistantService
from ..config.config import Config
from .assistant_response import apply_dragnet_filter
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def init_assistant():
    apply_dragnet_filter()
    try:
        assistant = AssistantService()
        if assistant and assistant.is_online:
            tier = getattr(Config, 'GEMINI_MODEL', 'Auto')
            logger.info(f"✅ AI Assistant Initialized - {tier}")
        else:
            logger.warning("⚠️ AI Assistant Initialized - OFFLINE Mode")
        return assistant
    except Exception as e:
        logger.exception(f"❌ AI Assistant Initialization Failed - {e}")
        return None
