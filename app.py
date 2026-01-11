import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "DEFAULT_SECRET_KEY")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "krishnav24-cs@sanskar.org")
bot, gh, li = None, None, None
try:
    print("⚙️  Loading Backend Systems...")
    from chat_bot.chat_bot import PortfolioChatBot
    from chat_bot.github import GitHubPortfolio
    from chat_bot.linkedin import LinkedInPortfolio
    bot = PortfolioChatBot()
    gh = GitHubPortfolio()
    li = LinkedInPortfolio()
    print("✅ Backend Systems Online")
    print("✅ Frontend Systems Online")
except ImportError as e:
    print(f"⚠️  Module Import Error: {e}")
    print("   (Running in 'Safe Mode' - Chatbot and API data will be disabled)")
except Exception as e:
    print(f"❌ Initialization Error: {e}")


@app.context_processor
def inject_status():
    """
    Injects 'is_ai_online' into every HTML template automatically.
    This allows the UI to show Red/Green dots based on backend status.
    """
    return dict(is_ai_online=(bot is not None))


@app.route('/')
def home():
    """Renders the Home Page."""
    return render_template('home.html')


@app.route('/about')
def about():
    """Renders the About Page, fetching profile data if available."""
    profile_data = {}
    if li:
        try:
            profile_data = li.get_profile()
        except Exception as e:
            print(f"Error fetching LinkedIn data: {e}")
    return render_template('about.html', profile=profile_data)


@app.route('/projects')
def projects():
    """Renders the Projects Page, fetching GitHub repos if available."""
    my_projects = []
    if gh:
        try:
            my_projects = gh.get_projects(sort_by="stars", limit=6)
        except Exception as e:
            print(f"Error fetching GitHub data: {e}")
    return render_template('projects.html', projects=my_projects)


@app.route('/skills')
def skills():
    """Renders the Skills Page."""
    return render_template('skills.html')


@app.route('/contact')
def contact():
    """Renders the Contact Page."""
    return render_template('contact.html', email=CONTACT_EMAIL)


@app.route('/get_response', methods=['POST'])
def get_bot_response():
    """
    Handles Chatbot interactions.
    """
    if not bot:
        return jsonify({"response": "⚠️ System Offline: The AI brain is currently disconnected. Please email Krishna directly."})
    data = request.get_json()
    user_msg = data.get('message')  
    if not user_msg:
        return jsonify({"response": "..."})
    try:
        ai_reply = bot.get_response(user_msg)
        return jsonify({"response": ai_reply})
    except Exception:
        return jsonify({"error": "All models exhausted"}), 429


if __name__ == '__main__':
    app.run(debug=True, port=5000)
