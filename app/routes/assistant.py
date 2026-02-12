import logging
from flask import Blueprint, request, jsonify, current_app, render_template
assistant_bp = Blueprint('assistant', __name__)
logger = logging.getLogger(__name__)


@assistant_bp.route('/assistant')
def assistant_page():
    """Renders the dedicated AI Assistant page."""
    return render_template('assistant.html', title="AI Assistant")


@assistant_bp.route('/get_status', methods=['GET'])
def get_status():
    """Returns the current operational status of the AI Assistant."""
    if hasattr(current_app, 'assistant') and current_app.assistant:
        if current_app.assistant.is_online:
            return jsonify({"status": "online"})
        else:
            return jsonify({"status": "database"})
    if hasattr(current_app, 'bot') and current_app.bot:
        if current_app.bot.is_online:
            return jsonify({"status": "online"})
        else:
            return jsonify({"status": "database"})
    return jsonify({"status": "offline"})


@assistant_bp.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"response": "I didn't Catch that. Could you repeat?"}), 400
    try:
        service = getattr(current_app, 'assistant',
                          getattr(current_app, 'bot', None))
        if not service:
            raise Exception("AI Service not initialized")
        response, status = service.get_response(user_input)
        if "online" in status:
            color_code = "\033[92m"
        elif "cached" in status:
            color_code = "\033[93m"
        elif "database" in status:
            color_code = "\033[33m"
        else:
            color_code = "\033[91m"
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
