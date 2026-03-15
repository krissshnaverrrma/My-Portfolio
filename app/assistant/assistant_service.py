import logging
import time
import hashlib
from google.genai import types
from ..config.config import Config
from ..db.data import (
    log_conversation, search_knowledge, get_ai_config,
    get_chat_history, get_all_knowledge, get_user_profile,
    get_cached_ai_response, set_cached_ai_response,
    get_all_posts, get_all_projects, get_all_certifications,
    get_all_skills, get_services, get_timeline, get_stats
)
from ..social.socials import GitHubPortfolio, LinkedInPortfolio
from .assistant_logic import (
    get_shared_client, get_valid_models, load_quick_responses,
    HEALTH_CHECK_QUERY
)
from .assistant_response import log_assistant_response
logger = logging.getLogger(__name__)


class AssistantService:
    def __init__(self):
        self.client = get_shared_client()
        self.ai_config = get_ai_config()
        self.model_stack = get_valid_models()
        self.is_online = bool(self.client and self.model_stack)
        self.quick_responses = load_quick_responses()
        self._CONTEXT_EXPIRY_HOURS = 1

    def get_response(self, user_input, session_id="default", silent=False):
        clean_input = user_input.strip().lower().replace("?", "").replace(".", "")
        recent_history = get_chat_history(session_id, limit=1)
        is_duplicate = False
        if recent_history and recent_history[0].user_query.strip().lower() == clean_input:
            is_duplicate = True
        if clean_input in self.quick_responses:
            reply = self.quick_responses[clean_input]
            if not silent:
                log_assistant_response(logger, "cached_mode", "Quick Response")
            if not is_duplicate:
                log_conversation(session_id, user_input, reply)
            return reply, "cached_mode"
        combined_prompt = f"ai_reply_{session_id}_{clean_input}"
        cache_key = hashlib.sha256(combined_prompt.encode()).hexdigest()
        cached_reply = get_cached_ai_response(cache_key)
        if cached_reply:
            if not silent:
                log_assistant_response(logger, "cached_mode")
            if not is_duplicate:
                log_conversation(session_id, user_input, cached_reply)
            return cached_reply, "cached_mode"
        if not self.is_online:
            return self._fallback_search(user_input)
        instructions = self._build_instructions()
        history = self._format_history(session_id)
        idx = 0
        backoff_time = 0.3
        while idx < len(self.model_stack):
            model_name = self.model_stack[idx]
            try:
                chat = self.client.chats.create(
                    model=model_name,
                    history=history,
                    config=types.GenerateContentConfig(
                        system_instruction=instructions,
                        temperature=0.7
                    )
                )
                response = chat.send_message(user_input)
                reply = response.text.strip()
                if not reply:
                    raise ValueError("Empty Response")
                set_cached_ai_response(cache_key, reply)
                if not is_duplicate:
                    log_conversation(session_id, user_input, reply)
                if not silent:
                    log_assistant_response(logger, "online", model_name)
                return reply, "online"
            except Exception as e:
                next_idx = idx + 1
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    logger.warning(
                        f"🔄 {model_name} Busy (Rate Limit Exceeded) - Switching in {backoff_time}s")
                    time.sleep(backoff_time)
                    backoff_time *= 2
                else:
                    logger.warning(f"⚠️ {model_name} Failed - {str(e)[:50]}")
                if next_idx >= len(self.model_stack):
                    break
                idx = next_idx
        return self._fallback_search(user_input)

    def _get_context(self):
        context_cache_key = "global_portfolio_context_string"
        cached_context = get_cached_ai_response(
            context_cache_key, expiry_hours=self._CONTEXT_EXPIRY_HOURS)
        if cached_context:
            return cached_context
        repo_text = "GitHub Data Temporarily Unavailable."
        try:
            gh = GitHubPortfolio()
            repos = gh.get_projects(limit=5)
            if repos:
                repo_text = "\n".join(
                    [f"- {r['name']}: {r['description']}" for r in repos])
        except Exception as e:
            logger.warning(f"⚠️ GitHub Context Failed - {e}")
        try:
            knowledge = get_all_knowledge()
            user = get_user_profile()
            posts = get_all_posts()
            projects = get_all_projects()
            certs = get_all_certifications()
            skills = get_all_skills()
            services = get_services()
            academic_timeline = get_timeline('academic')
            journey_timeline = get_timeline('journey')
            stats = get_stats()
            user_info = f"Name: {user.get('name', 'Krishna')} | Title: {user.get('title', 'Developer')} | Location: {user.get('location', 'Hapur')}\nPhilosophy/Bio: {user.get('philosophy', 'A passionate developer.')}"
            stats_text = f"Projects: {stats.get('projects_completed', 0)} | Certifications: {stats.get('certifications', 0)} | Commits: {stats.get('commits_made', 0)}"
            skills_text = ", ".join(
                [s.name for s in skills]) if skills else "Skills not listed."
            services_text = "\n".join(
                [f"- {s.title}: {s.description}" for s in services]) if services else "No services listed."
            timeline_text = "[ACADEMIC]\n" + "\n".join([f"- {t.year}: {t.title} at {t.subtitle}" for t in academic_timeline]) + \
                "\n\n[DEVELOPER JOURNEY]\n" + "\n".join(
                    [f"- {t.year}: {t.title} - {t.description}" for t in journey_timeline])
            db_text = "\n".join(
                [f"[{k.category}]: {k.info}" for k in knowledge])
            blog_text = "\n".join(
                [f"- {p.title}: {p.summary}" for p in posts]) if posts else "No Blog Posts Available."
            project_text = "\n".join(
                [f"- {p.title}: {p.description} (Tech: {p.tech_stack})" for p in projects]) if projects else "No Projects Available."
            cert_text = "\n".join(
                [f"- {c.title} by {c.issuer} ({c.status})" for c in certs]) if certs else "No Certifications Listed."
            context_string = (
                f"--- USER PROFILE & BIO ---\n{user_info}\n\n"
                f"--- PORTFOLIO STATS ---\n{stats_text}\n\n"
                f"--- TECHNICAL SKILLS ---\n{skills_text}\n\n"
                f"--- SERVICES OFFERED ---\n{services_text}\n\n"
                f"--- EXPERIENCE & EDUCATION ---\n{timeline_text}\n\n"
                f"--- GITHUB PROJECTS ---\n{repo_text}\n\n"
                f"--- PORTFOLIO PROJECTS ---\n{project_text}\n\n"
                f"--- CERTIFICATIONS ---\n{cert_text}\n\n"
                f"--- BLOG POSTS ---\n{blog_text}\n\n"
                f"--- EXTRA KNOWLEDGE BASE ---\n{db_text}\n\n"
                f"CONTACT EMAIL: {user.get('contact_email', user.get('email', 'N/A'))}"
            )
            set_cached_ai_response(context_cache_key, context_string)
            return context_string
        except Exception as e:
            logger.error(f"❌ Critical Context Build Error - {e}")
            return "Professional Backend Developer Context."

    def _build_instructions(self):
        base = self.ai_config.get("system_instruction", [
                                  "You are an assistant."])
        return "\n".join(base).replace("{context_data}", self._get_context())

    def _format_history(self, session_id):
        raw = get_chat_history(session_id)
        history = []
        for entry in raw:
            if not entry.user_query or not entry.bot_response or not entry.bot_response.strip():
                continue
            history.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=entry.user_query)]
            ))
            history.append(types.Content(
                role="model",
                parts=[types.Part.from_text(text=entry.bot_response)]
            ))
        return history

    def _fallback_search(self, query):
        matches = search_knowledge(query)
        if matches:
            log_assistant_response(logger, "database_mode")
            return "\n".join([f"• {m.info}" for m in matches]), "database_mode"
        log_assistant_response(logger, "offline")
        return "I am Currently Sleeping.", "offline"
