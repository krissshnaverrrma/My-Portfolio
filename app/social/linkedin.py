import logging
from typing import Dict, List, Any
from ..config.config import Config
from ..db.data import load_json_data
from ..utils.utils import load_json_file

logger = logging.getLogger(__name__)


class LinkedInPortfolio:
    def __init__(self):
        social_data = load_json_file(
            "app", "social", "social.json").get("linkedin", {})
        self.username: str = social_data.get(
            "username") or Config.LINKEDIN_USERNAME
        self.data: Dict[str, Any] = load_json_data().get("user_profile", {})
        self.profile: Dict[str, Any] = self.data.get("linkedin_profile", {})
        self.experience: List[Dict[str, Any]] = self.profile.get(
            "experience", []) if self.profile else []
        if "profile_url" not in self.profile and self.username:
            self.profile["profile_url"] = f"https://linkedin.com/in/{self.username}"

    def get_profile(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "profile": self.profile,
            "experience": self.experience
        }
