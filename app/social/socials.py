import requests
import json
import logging
from datetime import datetime
from ..config.config import Config
from ..db.data import get_data_json, get_cached_github_data, set_cached_github_data
logger = logging.getLogger(__name__)


def init_github():
    try:
        gh = GitHubPortfolio()
        if gh.username:
            if not Config.IS_RENDER:
                if Config.GITHUB_TOKEN:
                    logger.info(
                        f"✅ GitHub Service Initialized on Authenticated Mode for User: {gh.username}")
                else:
                    logger.warning(
                        f"⚠️ GitHub Service Initialized in Unauthenticated Mode for User: {gh.username}")
            return gh
        return None
    except Exception as e:
        logger.error(f"❌ Failed to Initialize GitHub Service: {e}")
        return None


def init_linkedin():
    try:
        li = LinkedInPortfolio()
        if li.username:
            if not Config.IS_RENDER:
                logger.info(
                    f"✅ LinkedIn Service Initialized for User: {li.username}")
            return li
        return None
    except Exception as e:
        logger.error(f"❌ Failed to Initialize LinkedIn Service: {e}")
        return None


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
