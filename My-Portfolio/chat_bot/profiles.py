import json
import os
import time
from datetime import datetime

import requests
from config import Config


class GitHubPortfolio:
    def __init__(self):
        self.username = Config.GITHUB_USERNAME
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        token = getattr(Config, 'GITHUB_TOKEN', None)
        if token:
            self.headers["Authorization"] = f"token {token}"
        else:
            pass
        self.cache_file = "github_cache.json"
        self.cache_duration = 3600

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self, data):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"❌ Cache Save Error: {e}")

    def get_profile(self):
        cache = self._load_cache()
        current_time = time.time()
        if "profile" in cache and (current_time - cache.get("profile_time", 0) < self.cache_duration):
            return cache["profile"]
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
            cache["profile"] = profile_data
            cache["profile_time"] = current_time
            self._save_cache(cache)
            return profile_data
        except Exception as e:
            print(f"❌ GitHub Profile Error: {e}")
            return cache.get("profile")

    def get_projects(self, sort_by="stars", limit=10):
        cache = self._load_cache()
        current_time = time.time()
        if "projects" in cache and (current_time - cache.get("projects_time", 0) < self.cache_duration):
            return cache["projects"][:limit]
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
            cache["projects"] = projects
            cache["projects_time"] = current_time
            self._save_cache(cache)
            return projects[:limit]

        except Exception as e:
            return cache.get("projects", [])[:limit]


class LinkedInPortfolio:
    def __init__(self):
        self.username = Config.LINKEDIN_USER
        self.profile = {
            "name": "Krishna Verma",
            "headline": "CS Student | Frontend & Backend Developer",
            "location": "Hapur, Uttar Pradesh, India",
            "about": "Computer Science undergraduate passionate about building scalable backend systems using Python.",
            "profile_url": f"https://www.linkedin.com/in/{self.username}"
        }
        self.experience = [{"role": "Computer Science Student", "company": "SCET",
                            "duration": "2024 - Present", "description": "Focusing on Data Structures and Web Technologies."}]

    def get_profile(self): return self.profile
    def get_experience(self): return self.experience
