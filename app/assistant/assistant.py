import logging
from .assistant_service import AssistantService
from ..config.config import Config
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def init_assistant():
    """
    Initializes the AI Assistant service and logs status updates.
    """
    print("📡 Contacting Gemini AI Studio to Initialize API Key...")
    try:
        assistant = AssistantService()
        if assistant and assistant.is_online:
            masked_key = assistant.get_masked_key()
            model_count = len(assistant.model_stack)
            tier = getattr(Config, 'GEMINI_MODEL', 'Auto')
            logger.info(f"Connecting to the GEMINI API Key: {masked_key}")
            logger.info(f"✅ AI Connected to GEMINI API Key: {masked_key}")
            logger.info(f"✅ AI Initialized on Tier: {tier}")
            logger.info(
                f"🚀 AI Initialized : {model_count} Models Available in Stack")
        else:
            logger.warning("⚠️ AI Assistant initialized in OFFLINE mode.")
        return assistant
    except Exception as e:
        logger.error(f"❌ Initialization Error: {str(e)}")
        logger.error(f"❌ Failed to Initialize Virtual AI Assistant: {e}")
        return None
