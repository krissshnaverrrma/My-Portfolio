import logging
from typing import Optional, List
from .github import GitHubPortfolio
from .linkedin import LinkedInPortfolio
from .contact import ContactInfo

logger = logging.getLogger(__name__)


class SocialServices:
    def __init__(self):
        self.github: Optional[GitHubPortfolio] = self._init_github()
        self.linkedin: Optional[LinkedInPortfolio] = self._init_linkedin()
        self.contact: Optional[ContactInfo] = self._init_contact()

    def _init_github(self) -> Optional[GitHubPortfolio]:
        try:
            temp_gh = GitHubPortfolio()
            if getattr(temp_gh, 'username', None):
                try:
                    temp_gh.get_projects(limit=12, sort_by="stars")
                except Exception as ge:
                    logger.warning(f"⚠️ GitHub Startup Fetch Failed: {ge}")
                return temp_gh
        except Exception as e:
            logger.error(f"❌ Failed to Load GitHub: {e}")
        return None

    def _init_linkedin(self) -> Optional[LinkedInPortfolio]:
        try:
            temp_li = LinkedInPortfolio()
            if getattr(temp_li, 'username', None):
                return temp_li
        except Exception as e:
            logger.error(f"❌ Failed to Load LinkedIn: {e}")
        return None

    def _init_contact(self) -> Optional[ContactInfo]:
        try:
            temp_contact = ContactInfo()
            if getattr(temp_contact, 'email', None) or getattr(temp_contact, 'phone', None):
                return temp_contact
        except Exception as e:
            logger.error(f"❌ Failed to Load Contact Info: {e}")
        return None

    @property
    def active_modules(self) -> List[str]:
        modules = []
        if self.github:
            modules.append("GitHub")
        if self.linkedin:
            modules.append("LinkedIn")
        if self.contact:
            modules.append("Contact")
        return modules


def setup_social_services() -> Optional[SocialServices]:
    try:
        services = SocialServices()
        active = services.active_modules
        if len(active) == 3:
            detail = "Active Modules"
        elif active:
            detail = f"Partially Active ({', '.join(active)} Only)"
        else:
            detail = "Offline"
        logger.info(f"✅ Social Info Initialized via {detail}")
        return services
    except Exception as e:
        logger.error(f"❌ Social Services Initialization Failed: {e}")
        return None


def init_socials() -> Optional[SocialServices]:
    return setup_social_services()
