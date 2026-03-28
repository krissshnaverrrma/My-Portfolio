import os
import re
import logging
from typing import Dict, List, Optional
from google import genai
from google.genai import types
from ..config import Config
from ..db import (
    get_ai_config, get_chat_history, get_all_database, get_user_profile,
    get_cached_ai_response, set_cached_ai_response,
    get_all_projects, get_all_posts, get_all_certifications,
    get_all_skills, get_services, get_timeline, get_stats,
    get_cached_valid_models, set_cached_valid_models
)
from ..social import GitHubPortfolio, LinkedInPortfolio
from ..utils import load_json_file

logger = logging.getLogger(__name__)


class AFCRewriter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "AFC is enabled" not in record.getMessage()


def apply_dragnet_filter() -> None:
    rewriter = AFCRewriter()
    root = logging.getLogger()
    for handler in root.handlers:
        handler.addFilter(rewriter)
    for log_obj in logging.root.manager.loggerDict.values():
        if isinstance(log_obj, logging.Logger):
            for handler in log_obj.handlers:
                handler.addFilter(rewriter)


def load_quick_responses() -> Dict[str, str]:
    try:
        raw_data = load_json_file("app", "assistant", "assistant.json") or {}
        return {k.strip().lower().replace("?", "").replace(".", ""): v for k, v in raw_data.items()}
    except Exception as e:
        logger.error(f"❌ Failed to Load Quick Responses: {e}")
        return {}


def get_valid_models() -> List[str]:
    if cached_models := get_cached_valid_models():
        return cached_models
    client = AssistantCoreLogic.get_shared_client()
    ai_config = get_ai_config()
    fallback_models = ai_config.get("fallback_models", [])
    env_preferred = os.getenv("GEMINI_MODEL")
    default_stack = [env_preferred] if env_preferred else []
    if not client:
        return default_stack + [m for m in fallback_models if m not in default_stack]
    try:
        api_response = client.models.list()
        available_names = {m.name.replace("models/", "") for m in api_response}
        valid_stack = [env_preferred] if (
            env_preferred and env_preferred in available_names) else []
        valid_stack.extend(
            [m for m in fallback_models if m in available_names and m not in valid_stack])
        if valid_stack:
            set_cached_valid_models(valid_stack)
            return valid_stack
    except Exception as e:
        logger.error(f"❌ Failed to Fetch Models from API: {e}")
    return default_stack + [m for m in fallback_models if m not in default_stack]


def is_query_relevant(query: str, ai_config: dict) -> bool:
    allowed_keywords = ai_config.get("allowed_keywords", ["krishna", "verma"])
    query_lower = query.lower()
    if query_lower in {"hi", "hello", "hey", "hola"}:
        return True
    pattern = re.compile(
        rf"\b({'|'.join(map(re.escape, allowed_keywords))})\b", re.IGNORECASE)
    return bool(pattern.search(query_lower))


class AssistantCoreLogic:
    _SHARED_CLIENT: Optional[genai.Client] = None

    def __init__(self):
        self.client = self.get_shared_client()
        self.ai_config = get_ai_config()
        self.model_stack = get_valid_models()
        self.is_online = bool(self.client and self.model_stack)
        self.quick_responses = load_quick_responses()
        self._CONTEXT_EXPIRY_HOURS = 1

    @classmethod
    def get_shared_client(cls) -> Optional[genai.Client]:
        if cls._SHARED_CLIENT is None and Config.GEMINI_API_KEY:
            try:
                cls._SHARED_CLIENT = genai.Client(
                    api_key=Config.GEMINI_API_KEY)
            except Exception as e:
                logger.error(f"❌ GenAI Client Error: {e}")
        return cls._SHARED_CLIENT

    def generate_content(self, model_name: str, instructions: str, history: List[types.Content], user_input: str) -> str:
        chat = self.client.chats.create(
            model=model_name,
            history=history,
            config=types.GenerateContentConfig(
                system_instruction=instructions,
                temperature=0.7
            )
        )
        return chat.send_message(user_input).text.strip()

    def build_instructions(self) -> str:
        base = self.ai_config.get("system_instruction", [
                                  "You are a Virtual AI Assistant."])
        return "\n".join(base).replace("{context_data}", self._get_context())

    def format_history(self, session_id: str) -> List[types.Content]:
        raw = get_chat_history(session_id)
        history = []
        for entry in raw:
            if not (entry.user_query and entry.bot_response and entry.bot_response.strip()):
                continue
            history.append(types.Content(role="user", parts=[
                           types.Part.from_text(text=entry.user_query)]))
            history.append(types.Content(role="model", parts=[
                           types.Part.from_text(text=entry.bot_response)]))
        return history

    def _get_context(self) -> str:
        cache_key = "GLOBAL_CONTEXT"
        if cached := get_cached_ai_response(cache_key, expiry_hours=self._CONTEXT_EXPIRY_HOURS):
            return cached
        try:
            user = get_user_profile() or {}
            stats = get_stats() or {}
            skills = get_all_skills() or []
            services = get_services() or []
            academic_tl = get_timeline('academic') or []
            journey_tl = get_timeline('journey') or []
            projects = get_all_projects() or []
            posts = get_all_posts() or []
            certs = get_all_certifications() or []
            database = get_all_database() or []
            try:
                github_repos = GitHubPortfolio().get_projects(limit=4) or []
            except Exception as e:
                logger.warning(f"⚠️ GitHub Portfolio Fetch Failed: {e}")
                github_repos = []

            def get_val(obj, attr_name):
                return getattr(obj, attr_name, "")

            def format_list(items, primary_attr, secondary_attr=None):
                if not items:
                    return "None"
                if secondary_attr:
                    return "\n".join(f"* {get_val(i, primary_attr)}: {get_val(i, secondary_attr)}" for i in items)
                return "\n".join(f"* {get_val(i, primary_attr)}" for i in items)
            blocks = [
                "[ PROFILE ]",
                f"Name: {user.get('name', 'Krishna')} | Title: {user.get('title', 'Developer')} | Location: {user.get('location', 'Hapur')}",
                f"Bio: {user.get('philosophy', 'A passionate developer.')}",
                f"Contact: {user.get('contact_email', user.get('email', 'N/A'))}",
                "",
                "[ STATS ]",
                f"Projects: {stats.get('projects_completed', 0)} | Certifications: {stats.get('certifications', 0)} | Commits: {stats.get('commits_made', 0)}",
                "",
                "[ SKILLS ]",
                " ".join(get_val(s, 'name')
                         for s in skills) or "None",
                "",
                "[ SERVICES ]",
                format_list(services, 'title', 'description'),
                "",
                "[ ACADEMIC ]",
                format_list(academic_tl, 'year', 'title'),
                "",
                "[ JOURNEY ]",
                format_list(journey_tl, 'year', 'title'),
                "",
                "[ GITHUB ]",
                "\n".join(
                    f"* {r.get('name', '')}: {r.get('description', '')}" for r in github_repos) or "None",
                "",
                "[ PROJECTS ]",
                format_list(projects, 'title'),
                "",
                "[ CERTIFICATIONS ]",
                format_list(certs, 'title'),
                "",
                "[ BLOGS ]",
                format_list(posts, 'title')
            ]
            if database:
                blocks.extend(["", "[ DATABASE ]", format_list(
                    database, 'category', 'info')])
            context_string = "\n".join(blocks).strip()
            set_cached_ai_response(cache_key, context_string)
            return context_string
        except Exception as e:
            logger.error(f"❌ Context Build Error: {e}")
            return "Professional Full Stack Developer Context."
