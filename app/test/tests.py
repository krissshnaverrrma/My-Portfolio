import pytest
import argparse
from flask import Flask
import sys
import os
import time
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.environ["FLASK_TESTING"] = "true"
try:
    from app import create_app
except ImportError:
    create_app = None


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    if not create_app:
        pytest.fail("Could not import 'create_app'. Check system path.")
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DEBUG": False,
        "GOOGLE_API_KEY": "test_key",
        "GITHUB_ACCESS_TOKEN": "test_token"
    })
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_config(app):
    """Test that the app is in testing mode."""
    assert app.config['TESTING'] is True


def test_home_page(client):
    """Test that the home page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Krishna" in response.data or b"Portfolio" in response.data


def test_projects_page(client):
    """Test that the projects page loads."""
    response = client.get('/projects')
    assert response.status_code in [200, 301, 308]


def test_404_page(client):
    """Test 404 error handler."""
    response = client.get('/non-existent-page')
    assert response.status_code == 404


def run_chat_mode():
    """Interactive CLI Chat with the Portfolio Assistant."""
    print("\n" + "─"*50)
    print("🤖 Krishna`s Virtual AI Assistant (CLI MODE)")
    print("─"*50)
    if not create_app:
        print("❌ Critical Error: App Factory not Found.")
        return
    os.environ["FLASK_TESTING"] = "false"
    app = create_app()
    with app.app_context():
        try:
            from app.assistant.assistant import init_assistant
            print("Connecting to AI Services...")
            ai_service = init_assistant()
            if not ai_service:
                print("\n❌ Error: Could not Connect to AI Service.")
                print("Check Internet Connection and API Keys in .env")
                return
            print("\n✅ System Online. Type 'exit' to quit.")
            print("─" * 50)
            while True:
                user_input = input("\n👤 You: ").strip()
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Shutting Down the System")
                    print("Switching to Offline Mode")
                    break
                if not user_input:
                    continue
                print("🤖 AI: Thinking...", end="\r")
                try:
                    if hasattr(ai_service, 'generate_response'):
                        response = ai_service.generate_response(user_input)
                    elif hasattr(ai_service, 'chat'):
                        response = ai_service.chat(user_input)
                    else:
                        response = f"[Mock] You said: {user_input}"
                    print(" " * 20, end="\r")
                    print(f"🤖 AI: {response}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
        except Exception as e:
            print(f"\n❌ Critical Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Portfolio Test & CLI Suite")
    parser.add_argument('--chat', action='store_true',
                        help="Launch Interactive AI Chat Mode")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Show full test output")
    args = parser.parse_args()
    if create_app is None:
        print("❌ FATAL: Could not import 'app'. System path broken.")
        sys.exit(1)
    if args.chat:
        run_chat_mode()
    else:
        print(f"\n🧪  Running System Diagnostics...", end=" ")
        pytest_args = ["-q", "--disable-warnings", "--tb=line", __file__]
        if args.verbose:
            pytest_args = ["-v", "--disable-warnings", __file__]
        start_time = time.time()
        result_code = pytest.main(pytest_args)
        duration = round(time.time() - start_time, 2)
        if result_code == 0:
            print(f"✅  PASSED ({duration}s)")
            print("All Systems Operational.")
            print("Now Try the Command : - flask run --debug")
        else:
            print(f"❌  FAILED ({duration}s)")
            print("    Review the Errors Above.")
        sys.exit(result_code)
