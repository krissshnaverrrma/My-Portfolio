import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print("✅ GEMINI_API_KEY found in .env file.")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env file.")
    exit()
genai.configure(api_key=api_key)


def list_available_models():
    """Lists all models available for content generation."""
    print(f"Using API Key: {api_key}")
    print("--- Checking Available Models ---")
    print("Active Models:")
    try:
        found_model = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ Active Models: {m.name}")
                found_model = True
        if not found_model:
            print("⚠️ No suitable text generation models found.")
    except Exception as e:
        print(f"❌ Error fetching models: {e}")


def test_model_connection(model_name="gemini-2.5-flash-lite"):
    """Tests a specific model with a simple prompt."""
    print(f"\n--- Testing Connection with {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            "Hello, this is a test check. Are you active?")
        if response and response.text:
            print(f"✅ Success! Model Response:\n{response.text}")
        else:
            print("⚠️ Model connected but returned empty response.")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")


if __name__ == "__main__":
    list_available_models()
    test_model_connection(
        os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash"))
