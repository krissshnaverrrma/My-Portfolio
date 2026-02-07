import logging
from .chat_bot_service import ChatBotService
from ..config.config import Config
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def init_bot():
    """
    Initializes the AI Assistant service for the web application.
    This function is called by the Flask app factory to enable the chat feature.
    """
    if not Config.GEMINI_API_KEY:
        logger.warning(
            "⚠️ GEMINI_API_KEY Missing. Initializing in Database/Offline mode.")
        return ChatBotService()
    try:
        bot = ChatBotService()
        logger.info(
            f"✅ Portfolio AI Assistant Initialized with {len(bot.model_stack)} Models.")
        return bot
    except Exception as e:
        logger.error(f"❌ Failed to Initialize  Virtual AI Assistant: {e}")
        return None
