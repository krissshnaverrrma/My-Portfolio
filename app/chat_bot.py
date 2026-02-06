import os
import sys
import argparse
import logging
from app.data import init_db
try:
    from app.chatbot_logic import PortfolioChatBot
except ImportError:
    from app.services.chatbot_logic import PortfolioChatBot
from app.config import Config

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def init_bot():
    if not Config.GEMINI_API_KEY:
        logger.warning(
            "⚠️ GEMINI_API_KEY not found. Bot will start in Offline Mode.")
        return None
    try:
        bot = PortfolioChatBot()
        logger.info("✅ AI Bot Services Initialized.")
        return bot
    except Exception as e:
        logger.error(f"❌ Critical Error: Bot initialization failed. {e}")
        return None


def run_diagnostics(bot):
    if not bot:
        logger.error("Diagnostic Fail: Bot is Offline.")
        return
    logger.info("Running Diagnostics...")
    try:
        response, status = bot.get_response("Hello")
        if status in ["success", "online"]:
            logger.info(
                f"✅ Diagnostics Passed: AI is Active (Mode: {status}).")
            logger.info(f"📝 Test Response: {response}")
        else:
            logger.warning(f"⚠️ Diagnostics Warning: Mode is {status}")
    except Exception as e:
        logger.error(f"❌ Diagnostics Failed: {e}")


def run_cli_mode(bot):
    """Interactive Chat Mode: Keep prints here for the User UI."""
    if not bot:
        print("❌ Error: Bot is Offline.")
        return
    print("\n🤖 Assistant Ready. Type 'exit' to stop.")
    while True:
        try:
            user_msg = input("You: ")
            if user_msg.lower() in ['exit', 'quit']:
                break
            ans, status = bot.get_response(user_msg)
            print(f"AI ({status}): {ans}\n")
        except KeyboardInterrupt:
            break
    print("👋 System Terminated Switching to Offline Mode.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Krishna's AI Assistant")
    parser.add_argument("--test", action="store_true", help="Run diagnostics")
    args = parser.parse_args()
    logger.info("Initializing Krishna's Virtual AI Assistant...")
    try:
        init_db()
    except Exception as e:
        logger.warning(f"Database Sync Warning: {e}")
    bot_instance = init_bot()
    if args.test:
        run_diagnostics(bot_instance)
    else:
        run_cli_mode(bot_instance)
