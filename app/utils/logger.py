import os
import sys
import logging
from ..config.config import Config


def configure_logging():
    """
    Configures Werkzeug logging and checks for CLI/Quiet modes.

    Returns:
        tuple: (is_cli_mode, is_quiet_mode)
    """
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    is_cli_mode = os.environ.get(
        "FLASK_CLI_MODE") == "true" or "cli.py" in sys.argv[0]
    quiet_commands = ["test", "hub"]
    is_quiet_mode = any(cmd in sys.argv for cmd in quiet_commands)
    if is_quiet_mode or Config.IS_RENDER:
        os.environ["FLASK_TESTING"] = "true"
        logging.disable(
            logging.WARNING if Config.IS_RENDER else logging.CRITICAL)
        os.environ["WERKZEUG_RUN_MAIN"] = "true"
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        logging.getLogger("flask").setLevel(logging.ERROR)
    return is_cli_mode, is_quiet_mode
