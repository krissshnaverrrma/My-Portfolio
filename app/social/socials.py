import requests
import json
import logging
from datetime import datetime
from ..config.config import Config
from ..db.database import get_db, APICache
from ..db.data import get_data_json
logger = logging.getLogger(__name__)


def init_github():
    """Initializes the GitHub Portfolio service with terminal logging."""
    try:
        gh = GitHubPortfolio()
        if gh.username:
            logger.info(
                f"✅ GitHub Service Initialized for User: {gh.username}")
            if Config.GITHUB_TOKEN:
                logger.info(
                    "GitHub API Initialized for Authenticated Mode")
            else:
                logger.warning(
                    "✅ GitHub API Initialized for Unauthenticated Mode")
            return gh
        return None
    except Exception as e:
        logger.error(f"❌ Failed to Initialize GitHub Service: {e}")
        return None


def init_linkedin():
    """Initializes the LinkedIn Portfolio service with terminal logging."""
    try:
        li = LinkedInPortfolio()
        if li.username:
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
        """
        Returns essential GitHub profile info for the home page.
        This provides the data expected by home.py to prevent AttributeErrors.
        """
        default_avatar = f"https://github.com/{self.username}.png"
        default_url = f"https://github.com/{self.username}"

        return {
            "username": self.username,
            "avatar_url": self.profile.get("avatar_url", default_avatar),
            "profile_url": self.profile.get("profile_url", default_url),
            "bio": self.profile.get("bio", ""),
            "api_status": "Authenticated" if Config.GITHUB_TOKEN else "Standard"
        }

    def _get_from_db(self, key):
        with get_db() as db:
            try:
                entry = db.query(APICache).filter_by(key=key).first()
                return entry
            except Exception as e:
                logger.error(f"⚠️ DB Cache Read Error: {e}")
                return None

    def _save_to_db(self, key, data):
        with get_db() as db:
            try:
                entry = db.query(APICache).filter_by(key=key).first()
                if entry:
                    entry.data = json.dumps(data)
                    entry.timestamp = datetime.utcnow()
                else:
                    db.add(APICache(key=key, data=json.dumps(data)))
                db.commit()
            except Exception as e:
                logger.error(f"⚠️ DB Cache Write Error: {e}")

    def get_projects(self, limit=6, sort_by="stars"):
        cache_key = f"github_repos_{self.username}_{sort_by}"
        cached_entry = self._get_from_db(cache_key)
        if cached_entry and (datetime.utcnow() - cached_entry.timestamp).total_seconds() < self.cache_duration:
            return json.loads(cached_entry.data)[:limit]
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
            self._save_to_db(cache_key, projects)
            return projects[:limit]
        except Exception:
            if cached_entry:
                return json.loads(cached_entry.data)[:limit]
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
        """
        Returns essential LinkedIn profile info for the home page.
        """
        return {
            "username": self.username,
            "profile_url": self.profile.get("profile_url"),
            "headline": self.profile.get("headline", "Computer Science Student"),
            "experience_count": len(self.experience)
        }
