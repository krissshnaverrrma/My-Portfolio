import logging
from typing import Dict
from ..config.config import Config
from ..utils.utils import load_json_file

logger = logging.getLogger(__name__)


class ContactInfo:
    def __init__(self):
        social_data = load_json_file(
            "app", "social", "social.json").get("contact", {})
        self.phone = social_data.get("phone") or Config.CONTACT_PHONE
        self.email = social_data.get("email") or Config.CONTACT_EMAIL

    def get_contact_card(self) -> Dict[str, str]:
        return {
            "email": self.email,
            "phone": self.phone,
        }
