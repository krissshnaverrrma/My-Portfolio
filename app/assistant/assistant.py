import logging
from .assistant_service import AssistantService
from ..config.config import Config

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def init_assistant():
    """
    Initializes the AI Assistant service and prints its configuration logic.
    This encapsulates the 'printing logic' previously in app.py.
    """
    logger.info("📡 Contacting Gemini AI Studio to Initialize API Key")
    try:
        assistant = AssistantService()
        masked_key = assistant.get_masked_key() if assistant else "None"
        model_count = len(assistant.model_stack) if assistant else 0
        tier = getattr(Config, 'GEMINI_MODEL', 'Auto')
        logger.info(f"✅ AI Connected to GEMINI API Key: {masked_key}")
        logger.info(f"✅ AI Initialized on Tier: {tier}")
        logger.info(f"✅ AI Assistant Initialized with {model_count} Models.")
        return assistant
    except Exception as e:
        logger.error(f"❌ Initialization Error: {str(e)}")
        logger.error(f"❌ Failed to Initialize Virtual AI Assistant: {e}")
        return None
