import os
import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
GITHUB_USERNAME = os.getenv("GITHUB_USER")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


class GitHubPortfolio:
    def __init__(self):
        if GITHUB_USERNAME:
            print("✅ GITHUB_USER found in .env file.")
        if not GITHUB_USERNAME:
            print("❌ Error: GITHUB_USER not found in .env file.")
        self.username = GITHUB_USERNAME
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {GITHUB_TOKEN}"
        else:
            print("Warning: No GITHUB_TOKEN found. API rate limits will be restricted.")

    def get_profile(self):
        """Fetches the user's profile information."""
        url = f"{self.base_url}/users/{self.username}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return {
                "name": data.get("name"),
                "bio": data.get("bio"),
                "avatar_url": data.get("avatar_url"),
                "profile_url": data.get("html_url"),
                "followers": data.get("followers"),
                "public_repos": data.get("public_repos"),
                "location": data.get("location")
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching profile: {e}")
            return None

    def get_projects(self, sort_by="stars", limit=6):
        """
        Fetches public repositories.
        sort_by: 'stars' or 'updated'
        """
        url = f"{self.base_url}/users/{self.username}/repos"
        params = {
            "sort": "pushed" if sort_by == "updated" else "full_name",
            "direction": "desc",
            "per_page": 100
        }
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            repos = response.json()
            my_repos = [repo for repo in repos if not repo["fork"]]
            if sort_by == "stars":
                my_repos.sort(
                    key=lambda x: x["stargazers_count"], reverse=True)
            elif sort_by == "updated":
                my_repos.sort(key=lambda x: x["pushed_at"], reverse=True)
            projects = []
            for repo in my_repos[:limit]:
                projects.append({
                    "name": repo["name"],
                    "description": repo["description"] or "No description provided.",
                    "language": repo["language"] or "Code",
                    "stars": repo["stargazers_count"],
                    "url": repo["html_url"],
                    "updated_at": datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%b %d, %Y")
                })
            return projects
        except requests.exceptions.RequestException as e:
            print(f"Error fetching projects: {e}")
            return []


if __name__ == "__main__":
    try:
        gh = GitHubPortfolio()
        print(f"Fetching data for: {gh.username}")
        profile = gh.get_profile()
        if profile:
            print(f"\nUser: {profile['name']}")
            print(f"Bio: {profile['bio']}")
        print("\n--- Top Projects ---")
        projects = gh.get_projects(sort_by="stars", limit=10)
        for p in projects:
            print(f"-> {p['name']} ({p['stars']} stars)")
    except ValueError as e:
        print(e)
