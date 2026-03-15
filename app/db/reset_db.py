import app.db.models as models  # Load all models to identify tables
from app.db.database import engine, Base
import logging
import sys
import os
from sqlalchemy import text

# Adjusting path to find the 'app' module correctly
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def wipe_database_headless():
    # Only run if the user provides a specific flag to prevent accidental wipes
    force = os.getenv("CONFIRM_RESET", "False").lower() == "true"

    logger.info("☢️  HEADLESS DATABASE RESET INITIALIZED")

    if force:
        try:
            logger.info(
                "Connecting to database and dropping all registered tables...")
            # Drops everything currently in your models.py
            Base.metadata.drop_all(bind=engine)

            # Manually drop the 'api_cache' ghost table if it still exists
            with engine.connect() as conn:
                conn.execute(text('DROP TABLE IF EXISTS "api_cache" CASCADE;'))
                conn.commit()

            logger.info(
                "✅ SUCCESS: Database wiped clean. Ghost tables removed.")
        except Exception as e:
            logger.error(f"❌ RESET FAILED: {e}")
    else:
        logger.warning(
            "❌ RESET ABORTED: 'CONFIRM_RESET' env var is not set to 'True'.")


if __name__ == "__main__":
    wipe_database_headless()
