import logging
from flask import url_for

logger = logging.getLogger(__name__)


class DiagnosticEngine:
    BOLD, GREEN, RED, BLUE, END = "\033[1m", "\033[92m", "\033[91m", "\033[94m", "\033[0m"

    def __init__(self, app):
        self.app = app

    def run_route_audit(self):
        """Dynamically audits every registered route in the application."""
        all_endpoints = [
            rule.endpoint for rule in self.app.url_map.iter_rules()
            if 'static' not in rule.endpoint
        ]

        passed = 0
        with self.app.test_request_context():
            for endpoint in all_endpoints:
                try:
                    url_for(endpoint, slug='test-slug',
                            name='test-user', _external=False)
                    passed += 1
                except:
                    continue

        if passed == len(all_endpoints):
            print(
                f"{self.GREEN}✅ DIAGNOSTICS Audit: All {passed} Registered Routes are Initialized Correctly.{self.END}")
            return True
        return False
