import json
import os
from flask import Blueprint, render_template
resume_bp = Blueprint('resume', __name__)


def load_portfolio_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, 'db', 'data.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@resume_bp.route('/resume')
def resume_page():
    data = load_portfolio_data()
    return render_template('resume.html', **data)


@resume_bp.route('/resume_print')
def resume_detail():
    data = load_portfolio_data()
    return render_template('resume_detail.html', **data)
