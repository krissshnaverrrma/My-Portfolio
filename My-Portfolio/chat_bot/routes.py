import os

from chatbot_logic import PortfolioChatBot
from config import Config
from database import BlogPost, SessionLocal, get_all_posts, init_db
from flask import Blueprint, abort, jsonify, render_template, request
from profiles import GitHubPortfolio, LinkedInPortfolio

main_bp = Blueprint('main', __name__)
print("⚙️ Loading All the Systems...")
try:
    init_db()
    bot = PortfolioChatBot()
    gh = GitHubPortfolio()
    li = LinkedInPortfolio()
    print("✅ Routes Activated: Systems Ready.")
except Exception as e:
    print(f"❌ Route System Error: {e}")
    bot, gh, li = None, None, None


@main_bp.context_processor
def inject_globals():
    """Injects data like AI status and contact info into every template."""
    return {
        "is_ai_online": (bot is not None),
        "contact_email": getattr(Config, 'CONTACT_EMAIL', os.getenv("CONTACT_EMAIL"))
    }


@main_bp.route('/')
def home():
    """Renders the Index/Home Page with profile data."""
    gh_profile = gh.get_profile() if gh else {}
    li_profile = li.get_profile() if li else {}
    return render_template('home.html', gh=gh_profile, li=li_profile)


@main_bp.route('/about')
def about():
    """Renders the About Page."""
    profile_data = li.get_profile() if li else {}
    return render_template('about.html', profile=profile_data)


@main_bp.route('/projects')
def projects():
    """Renders the Projects Page with GitHub repos."""
    my_projects = []
    if gh:
        try:
            my_projects = gh.get_projects(sort_by="stars", limit=10)
        except Exception as e:
            print(f"Error fetching projects: {e}")
    return render_template('projects.html', projects=my_projects)


@main_bp.route('/blog')
def blog():
    """Renders blog.html with all posts."""
    posts = get_all_posts()
    return render_template('blog.html', posts=posts)


@main_bp.route('/blog/<slug>')
def blog_detail(slug):
    """Renders blog_detail.html for a specific post."""
    db = SessionLocal()
    try:
        post = db.query(BlogPost).filter(BlogPost.slug == slug).first()
        if not post:
            abort(404)
        return render_template('blog_detail.html', post=post)
    finally:
        db.close()


@main_bp.route('/get_response', methods=['POST'])
def get_bot_response():
    """Handles Chatbot interactions for the Web UI."""
    if not bot:
        return jsonify({"response": "System is offline.", "status": "offline"})
    data = request.get_json()
    user_msg = data.get('message', '')
    if not user_msg:
        return jsonify({"response": "Empty message.", "status": "error"})
    try:
        reply, status = bot.get_response(user_msg)
        return jsonify({"response": reply, "status": status})
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({"response": "Error processing request.", "status": "error"}), 500


@main_bp.route('/skills')
def skills():
    return render_template('skills.html')


@main_bp.route('/resume')
def resume_page():
    return render_template('resume.html')


@main_bp.route('/contact')
def contact():
    email = getattr(Config, 'CONTACT_EMAIL', os.getenv("CONTACT_EMAIL"))
    return render_template('contact.html', email=email)


@main_bp.route('/certificate')
def certificate():
    name = request.args.get('name', 'Krishna Verma')
    return render_template('certificate.html', name=name)
