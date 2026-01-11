import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask import jsonify
from chat_bot.github import GitHubPortfolio
from chat_bot.linkedin import LinkedInPortfolio
from chat_bot.database import get_all_knowledge, log_conversation
from chat_bot.ai_model_manager import ModelManager
load_dotenv()

class PortfolioChatBot:
    def __init__(self):
        print("Initializing AI Brain...")
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            print("✅ GEMINI_API_KEY found in .env file.")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        genai.configure(api_key=api_key)
        self.context_data = self._gather_context()
        self.system_instruction = f"""
        You are an AI Assistant for Krishna Verma's personal portfolio website.
        Your goal is to answer visitor questions professionally, concisely, and enthusiastically.
        HERE IS KRISHNA'S DATA (Use this to answer):
        {self.context_data}
        RULES:1. **Identity**: You are an assistant. Refer to Krishna in the third person (He/Him).
        2. **Tone**: Professional, enthusiastic, and concise.
        3. **Constraints (CRITICAL)**: 
           - If the user asks for a specific length (e.g., "in 50 words", "short summary"), **YOU MUST STRICTLY FOLLOW THAT LIMIT**.
           - If no length is specified, keep answers under 3 sentences.
        4. **Scope**: Only answer questions about Krishna's skills, projects, and experience and their personal details. If asked about general topics (like "who is the president"), politely refuse.
        - If asked about something not in the data, say you don't know but suggest contacting Krishna.
        - Keep answers short (under 3-4 sentences) unless asked for details.
        - Be friendly and engaging and also a frank and open-minded assistant.
        - Do not make up facts.
        """
        self.model = genai.GenerativeModel(
            model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            system_instruction=self.system_instruction
        )   
        self.chat_session = self.model.start_chat(history=[])

    def _gather_context(self):
        """Helper to fetch and format all data into a text block for the AI."""
        try:
            gh = GitHubPortfolio()
            li = LinkedInPortfolio()
            gh_profile = gh.get_profile()
            gh_projects = gh.get_projects(limit=5)
            db_knowledge = get_all_knowledge()
            li_profile = li.get_profile()
            li_experience = li.get_experience()
            data_str = "--- PROFILE ---\n"
            data_str += f"Name: {li_profile['name']}\n"
            data_str += f"Bio: {li_profile['headline']}\n"
            data_str += f"About: {li_profile['about']}\n"
            data_str += f"Location: {li_profile['location']}\n\n"
            data_str += "--- EXPERIENCE ---\n"
            for job in li_experience:
                data_str += f"- Role: {job['role']} at {job['company']} ({job['duration']}). Details: {job['description']}\n"
            data_str += "\n--- TOP PROJECTS (GitHub) ---\n"
            for p in gh_projects:
                data_str += f"- Project Name: {p['name']}\n"
                data_str += f"  Description: {p['description']}\n"
                data_str += f"  Tech: {p['language']} | Stars: {p['stars']}\n"
            data_str += db_knowledge
            return data_str
        except Exception as e:
            return f"Error loading data: {e}. (Please answer generally)."

    def get_response(self, user_input):
        """Sends user message to Gemini and gets the reply."""
        try:
            response = self.chat_session.send_message(user_input)
            reply_text = response.text.strip()
            log_conversation(user_input, reply_text)
            return reply_text
        except Exception as e:
            print(f"\n[DEBUG ERROR]: {e}\n")
            return "Currently Sleeping. Please Contact Krishna Directly on Email."


if __name__ == "__main__":
    bot = PortfolioChatBot()
    print("\n🤖 AI Assistant Ready! (Type 'quit' to exit)")
    while True:
        user_in = input("\nYou: ")
        if user_in.lower() in ["quit", "exit"]:
            break
        print("Bot is thinking...", end="\r")
        reply = bot.get_response(user_in)
        print(f"Bot: {reply}")
