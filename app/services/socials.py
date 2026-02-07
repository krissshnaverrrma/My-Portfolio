import requests
import json
import logging
from datetime import datetime
from ..config.config import Config
from ..db.database import get_db, APICache
from ..db.data import get_data_json
logger = logging.getLogger(__name__)


class GitHubPortfolio:
    def __init__(self):
        self.username = Config.GITHUB_USERNAME
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if Config.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {Config.GITHUB_TOKEN}"
        self.cache_duration = 3600

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
                logger.error(f"❌ DB Cache Save Error: {e}")
                db.rollback()

    def get_profile(self):
        cache_key = "github_profile"
        cached_entry = self._get_from_db(cache_key)
        if cached_entry:
            age = (datetime.utcnow() - cached_entry.timestamp).total_seconds()
            if age < self.cache_duration:
                return json.loads(cached_entry.data)
        url = f"{self.base_url}/users/{self.username}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            profile_data = {
                "name": data.get("name"),
                "bio": data.get("bio"),
                "avatar_url": data.get("avatar_url"),
                "profile_url": data.get("html_url")
            }
            self._save_to_db(cache_key, profile_data)
            return profile_data
        except Exception:
            if cached_entry:
                return json.loads(cached_entry.data)
            return {}

    def get_projects(self, sort_by="stars", limit=10):
        cache_key = "github_projects"
        cached_entry = self._get_from_db(cache_key)
        if cached_entry:
            return json.loads(cached_entry.data)[:limit]
        url = f"{self.base_url}/users/{self.username}/repos"
        try:
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
            self.profile["profile_url"] = f"https://www.linkedin.com/in/{self.username}"

    def get_profile(self): return self.profile
    def get_experience(self): return self.experience
