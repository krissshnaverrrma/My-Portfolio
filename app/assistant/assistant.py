import logging
from .assistant_service import AssistantService
from ..config.config import Config


class AFCRewriter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        if "AFC is enabled" in msg:
            try:
                count = msg.split(":")[-1].strip().replace(".", "")
            except:
                count = "N/A"
            print(
                f"INFO: ✅ AI Function Calling Enabled (Max Parallel Calls: {count})")
            return False
        return True


def apply_dragnet_filter():
    """
    Iterates through EVERY logger and handler in the system to attach the filter.
    """
    rewriter = AFCRewriter()
    root = logging.getLogger()
    root.addFilter(rewriter)
    for h in root.handlers:
        h.addFilter(rewriter)
    targets = ["werkzeug", "flask", "google",
               "google.genai", "urllib3", "httpcore", "httpx"]
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


apply_dragnet_filter()
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def init_assistant():
    """
    Initializes the AI Assistant service and logs status updates.
    """
    apply_dragnet_filter()
    try:
        assistant = AssistantService()
        if assistant and assistant.is_online:
            masked_key = assistant.get_masked_key()
            model_count = len(assistant.model_stack)
            tier = getattr(Config, 'GEMINI_MODEL', 'Auto')
            logger.info(
                f"✅ AI Initialized on {tier} Tier via Key {masked_key} and Available Models Counted as {model_count}")
        else:
            logger.warning("⚠️ AI Assistant Initialized in OFFLINE Mode.")
        return assistant
    except Exception as e:
        logger.error(f"❌ Initialization Error: {str(e)}")
        logger.error(f"❌ Failed to Initialize Virtual AI Assistant: {e}")
        return None
