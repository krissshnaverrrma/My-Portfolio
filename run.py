import os
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import create_app
app = create_app()
if __name__ == "__main__":
    is_render = os.environ.get("RENDER") == "true"
    host = "0.0.0.0" if is_render else os.environ.get(
        "FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", os.environ.get("FLASK_RUN_PORT", 5000)))
    debug_mode = not is_render
    if not is_render and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        print(f"Server Running at: http://{host}:{port}")
    app.run(debug=debug_mode, host=host, port=port)
