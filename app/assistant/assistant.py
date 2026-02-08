import logging
from .assistant_service import AssistantService
from ..config.config import Config

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def init_assistant():
    """
    Initializes the AI Assistant service and logs status updates.
    """
    logger.info("📡 Contacting Gemini AI Studio to Initialize API Key")
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
                f"✅ Integrating {model_count} Valid AIModels in Stack")
            logger.info(
                f"✅ Success : {model_count} AI Models Integrated in Stack")
        else:
            logger.warning("⚠️ AI Assistant initialized in OFFLINE mode.")
        return assistant
    except Exception as e:
        logger.error(f"❌ Initialization Error: {str(e)}")
        logger.error(f"❌ Failed to Initialize Virtual AI Assistant: {e}")
        return None


def verify_assistant_health(assistant):
    """
    Performs a self-diagnostic check on the assistant.
    This logic triggers the 'Smart Cache' log by invoking a test response.
    """
    try:
        res, mode = assistant.get_response("Who are you?")
        is_healthy = any(w in res.lower()
                         for w in ["assistant", "virtual", "krishna"])
        return is_healthy, mode
    except Exception as e:
        logger.error(f"❌ Assistant Diagnostic Failed: {e}")
        return False, "offline"
