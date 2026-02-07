import logging
from flask import Blueprint, request, jsonify, current_app
chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)


@chat_bp.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"response": "I didn't Catch that. Could you repeat?"}), 400
    try:
        response, status = current_app.bot.get_response(user_input)
        color_code = "\033[92m" if "online" in status else "\033[93m"
        reset_code = "\033[0m"
        logger.info(
            f"🤖 {color_code}AI Response Generated Via: {status}{reset_code}")
        return jsonify({
            "response": response,
            "status": status
        })
    except Exception as e:
        logger.error(f"❌ Chat Route Error: {e}")
        return jsonify({"response": "System is temporarily unavailable."}), 500
