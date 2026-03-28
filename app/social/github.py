import logging
import requests
from datetime import datetime
from typing import Dict, List, Any
from ..config.config import Config
from ..db.data import get_cached_github_data, set_cached_github_data, CacheKeys
from ..utils.utils import load_json_file

logger = logging.getLogger(__name__)


class GitHubPortfolio:
    def __init__(self):
        social_data = load_json_file(
            "app", "social", "social.json").get("github", {})
        self.username: str = social_data.get(
            "username") or Config.GITHUB_USERNAME
        self.token: str = social_data.get("token") or Config.GITHUB_TOKEN
        self.base_url: str = f"https://api.github.com/users/{self.username}/repos"

    def get_projects(self, limit: int = 12, sort_by: str = "stars") -> List[Dict[str, Any]]:
        if not self.username:
            return []
        social_data = load_json_file(
            "app", "social", "social.json").get("github", {})
        json_projects = social_data.get("projects")
        if json_projects and isinstance(json_projects, list):
            return json_projects[:limit]
        cache_key = f"{CacheKeys.GITHUB_REPOS}_{self.username}_{limit}_{sort_by}"
        cached_data = get_cached_github_data(cache_key)
        if cached_data:
            return cached_data
        try:
            headers = {"Accept": "application/vnd.github.v3+json"}
            if self.token:
                headers["Authorization"] = f"token {self.token}"
            response = requests.get(self.base_url, headers=headers, timeout=10)
            response.raise_for_status()
            repos = response.json()
            my_repos = [repo for repo in repos if not repo.get("fork", False)]
            if sort_by == "stars":
                my_repos.sort(key=lambda x: x.get(
                    "stargazers_count", 0), reverse=True)
            projects = []
            for r in my_repos:
                try:
                    updated_str = datetime.strptime(
                        r.get("pushed_at", ""), "%Y-%m-%dT%H:%M:%SZ"
                    ).strftime("%b %d, %Y")
                except Exception:
                    updated_str = "Unknown"
                projects.append({
                    "name": r.get("name", "Unknown"),
                    "description": r.get("description") or "No description provided.",
                    "language": r.get("language") or "Code",
                    "stars": r.get("stargazers_count", 0),
                    "url": r.get("html_url", "#"),
                    "updated_at": updated_str
                })
            final_projects = projects[:limit]
            set_cached_github_data(cache_key, final_projects)
            return final_projects
        except requests.exceptions.RequestException as e:
            logger.error(f"⚠️ GitHub API Network Error: {e}")
        except Exception as e:
            logger.error(f"⚠️ GitHub Data Processing Error: {e}")
        return []
