import importlib
import os
import sys

from dotenv import load_dotenv
from flask import Flask

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAT_BOT_DIR = os.path.join(BASE_DIR, 'chat_bot')
if CHAT_BOT_DIR not in sys.path:
    sys.path.insert(0, CHAT_BOT_DIR)
load_dotenv()
config_module = importlib.import_module("config")
routes_module = importlib.import_module("routes")
Config = config_module.Config
main_bp = routes_module.main_bp
app = Flask(__name__)
app.secret_key = getattr(Config, 'SECRET_KEY',
                         os.getenv("FLASK_SECRET_KEY", "dev_key"))
app.register_blueprint(main_bp)
if __name__ == '__main__':
    print("🚀 Starting Flask Server...")
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)
