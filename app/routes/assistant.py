import uuid
import logging
from flask import Blueprint, request, jsonify, current_app, render_template, session
from ..system.systems import limiter
from ..assistant.assistant_response import log_assistant_response
assistant_bp = Blueprint('assistant', __name__)

logger = logging.getLogger(__name__)


@assistant_bp.route('/assistant')
def assistant_page():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('assistant.html', title="AI Assistant")


@assistant_bp.route('/get_status', methods=['GET'])
def get_status():
    if hasattr(current_app, 'assistant') and current_app.assistant:
        if current_app.assistant.is_online:
            return jsonify({"status": "online"})
        else:
            return jsonify({"status": "database"})
    return jsonify({"status": "offline"})


@assistant_bp.route('/get_response', methods=['POST'])
@limiter.limit("15 per minute")
def get_response():
    user_input = request.json.get('message')
    if not user_input or len(user_input.strip()) == 0:
        return jsonify({"response": "I didn't catch that."}), 400
    if len(user_input) > 500:
        return jsonify({"response": "Your Message is too Long. Please Keep it under 500 Characters."}), 400
    session_id = session.get('session_id', str(uuid.uuid4()))
    try:
        service = getattr(current_app, 'assistant',
                          getattr(current_app, 'bot', None))
        if not service:
            raise Exception("AI Assistant Service not Initialized")
        response, status = service.get_response(
            user_input, session_id=session_id)
        return jsonify({
            "response": response,
            "status": status
        })
    except Exception as e:
        logger.error(f"❌ Chat Route Error: {e}")
        return jsonify({"response": "System is Temporarily Unavailable."}), 500
