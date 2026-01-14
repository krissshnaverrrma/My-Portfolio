import os
import sys

from chatbot_logic import PortfolioChatBot
from config import Config

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

if __name__ == "__main__":
    print("🚀 Initializing Krishna's Virtual AI Assistant...")
    if Config.GEMINI_API_KEY:
        try:
            bot = PortfolioChatBot()
            print("✅ Bot Initialized Successfully.")
            print("\n🤖 Assistant Ready. Type 'exit' to stop.")
            while True:
                try:
                    user_msg = input("You: ")
                    if user_msg.lower() in ['exit', 'quit']:
                        break
                    ans, status = bot.get_response(user_msg)
                    print(f"AI ({status.upper()}): {ans}")
                except KeyboardInterrupt:
                    break
            print("👋 Exiting...")
        except Exception as e:
            print(f"❌ Bot Crash: {e}")
    else:
        print("❌ Error: Currently Sleeping.")
