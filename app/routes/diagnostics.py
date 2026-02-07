import time
from flask import Blueprint, jsonify, current_app, request
from ..runtime.runtime import PortfolioRuntime, SystemHealth
diag_bp = Blueprint('diagnostics', __name__)


@diag_bp.route('/system/health')
def health_dashboard():
    if not current_app.debug and request.args.get('key') != "lazy-coder-secret":
        return jsonify({"error": "Unauthorized"}), 403
    health = SystemHealth(current_app.bot)
    health.run_full_diagnostic()
    if request.args.get('stress') == 'true':
        health.run_stress_test()
    return jsonify({
        "system": "Krishna's Portfolio",
        "timestamp": time.time(),
        "report": health.results
    })
