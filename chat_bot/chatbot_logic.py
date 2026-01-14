import os
import sys

from ai_logic import ModelManager
from database import get_all_knowledge
from profiles import GitHubPortfolio, LinkedInPortfolio

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class PortfolioChatBot:
    def __init__(self):
        self.context_data = self._load_everything()
        self.system_instruction = f"""
        You are the Virtual AI Assistant for Krishna Verma.
        CORE ROLE:
        You are NOT Krishna. You are his intelligent assistant. 
        Your job is to introduce him, showcase his work, and answer questions about him.
        ALWAYS refer to Krishna as "He", "Him", "The Developer", or "Krishna".
        NEVER say "I" when referring to his skills or projects.
        KRISHNA'S "LAZY CODER" PHILOSOPHY:
        Krishna embodies the 'Lazy Coder' mentality.
        - His Belief: "If a task needs to be done twice, it should be automated."
        - His Focus: He writes clean, modular code that works harder so he doesn't have to.
        - His Goal: Cutting redundancy, optimizing algorithms, and building self-sustaining backend systems.
        ABOUT KRISHNA:
        - Education: Computer Science Undergraduate at Sanskar College of Engineering and Technology (SCET), Ghaziabad.
        - Tech Stack: Passionate about scalable backends (PostgreSQL) and interactive frontends (Flask).
        - Interests: Chess (Strategic planning), Open Source, and writing guides.
        DYNAMIC CONTEXT (Use this to answer specific questions):
        {self.context_data}
        GUIDELINES:
        - Tone: Professional, polite, yet frank and efficient.
        - If asked "Who are you?", say: "I am Krishna's AI Assistant."
        - If asked "Who is Krishna?", describe him using the details above.
        """
        self.model_manager = ModelManager(
            system_instruction=self.system_instruction)

    def _load_everything(self):
        try:
            gh, li, knowledge = GitHubPortfolio(), LinkedInPortfolio(), get_all_knowledge()
            repos = gh.get_projects(limit=5)
            repo_text = "\n".join(
                [f"- {r['name']}: {r['description']}" for r in repos])
            db_text = "\n".join([f"{k.category}: {k.info}" for k in knowledge])
            return f"GITHUB: {repo_text}\nLINKEDIN: {li.get_profile().get('about')}\nDB: {db_text}"
        except:
            return "Krishna is a Full Stack Developer."

    def get_response(self, user_input):
        return self.model_manager.generate_response(user_input)
