import requests
import json
import logging
from datetime import datetime
from ..config.config import Config
from ..db.data import get_data_json, get_cached_github_data, set_cached_github_data
logger = logging.getLogger(__name__)


def init_socials():
    try:
        services = SocialServices()
        detail = "Contacts Linked" if services.contact else "Standard Mode"
        logger.info(f"✅ Social Services Initialized - {detail}")
        return services
    except Exception as e:
        logger.error(f"❌ Social Services Initialization Failed - {e}")
        return None


class SocialServices:
    def __init__(self):
        self.github = None
        self.linkedin = None
        self.contact = None
        try:
            temp_gh = GitHubPortfolio()
            if temp_gh.username:
                self.github = temp_gh
        except Exception as e:
            logger.error(f"❌ Failed to Load GitHub: {e}")
        try:
            temp_li = LinkedInPortfolio()
            if temp_li.username:
                self.linkedin = temp_li
        except Exception as e:
            logger.error(f"❌ Failed to Load LinkedIn: {e}")
        try:
            temp_contact = ContactInfo()
            if temp_contact.email or temp_contact.phone:
                self.contact = temp_contact
        except Exception as e:
            logger.error(f"❌ Failed to Load Contact Info: {e}")


class ContactInfo:
    def __init__(self):
        self.email = Config.CONTACT_EMAIL
        self.phone = Config.CONTACT_PHONE
        self.data = get_data_json()
        self.profile = self.data.get("contact_profile", {})

    def get_profile(self):
        return {
            "email": self.email or self.profile.get("email", "No email provided"),
            "phone": self.phone or self.profile.get("phone", "No phone provided")
        }


class GitHubPortfolio:
    def __init__(self):
        self.data = get_data_json()
        self.profile = self.data.get("github_profile", {})
        self.username = self.profile.get("username", Config.GITHUB_USERNAME)
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if Config.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {Config.GITHUB_TOKEN}"
        self.cache_duration = 3600

    def get_profile(self):
        default_avatar = f"https://github.com/{self.username}.png"
        default_url = f"https://github.com/{self.username}"
        return {
            "username": self.username,
            "avatar_url": self.profile.get("avatar_url", default_avatar),
            "profile_url": self.profile.get("profile_url", default_url),
            "bio": self.profile.get("bio", ""),
            "api_status": "Authenticated" if Config.GITHUB_TOKEN else "Standard"
        }

    def get_projects(self, limit=6, sort_by="stars"):
        cache_key = f"github_repos_{self.username}_{sort_by}"
        cached_data = get_cached_github_data(
            cache_key, expiry_seconds=self.cache_duration)
        if cached_data:
            return cached_data[:limit]
        try:
            url = f"{self.base_url}/users/{self.username}/repos"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            repos = response.json()
            my_repos = [repo for repo in repos if not repo["fork"]]
            if sort_by == "stars":
                my_repos.sort(
                    key=lambda x: x["stargazers_count"], reverse=True)
            projects = [{
                "name": r["name"],
                "description": r["description"] or "No description provided.",
                "language": r["language"] or "Code",
                "stars": r["stargazers_count"],
                "url": r["html_url"],
                "updated_at": datetime.strptime(r["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%b %d, %Y")
            } for r in my_repos]
            set_cached_github_data(cache_key, projects)
            return projects[:limit]
        except Exception as e:
            logger.error(f"⚠️ GitHub API Fetch Error: {e}")
            return []


class LinkedInPortfolio:
    def __init__(self):
        self.username = Config.LINKEDIN_USER
        self.data = get_data_json()
        self.profile = self.data.get("linkedin_profile", {})
        self.experience = self.profile.get("experience", [])
        if "profile_url" not in self.profile:
            self.profile["profile_url"] = f"https://linkedin.com/in/{self.username}"

    def get_profile(self):
        return {
            "username": self.username,
            "profile_url": self.profile.get("profile_url"),
            "headline": self.profile.get("headline", "Computer Science Student"),
            "experience_count": len(self.experience)
        }
