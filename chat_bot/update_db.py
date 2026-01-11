from sqlalchemy import text
from database import engine, init_db


def fix_table():
    print("--- 🛠 Fixing Database Schema ---")

    with engine.connect() as conn:
        conn.begin()
        try:
            sql = text("ALTER TABLE blog_posts ADD COLUMN image_url VARCHAR;")
            conn.execute(sql)
            print("✅ Successfully Added 'image_url' column!")
        except Exception as e:
            print(f"⚠️ Note: {e}")
            print(
                "   (This usually means the column already exists or table is missing.)")

    print("🔄 Verifying Tables...")
    init_db()
    print("--- 🚀 Database Patch Complete ---")


if __name__ == "__main__":
    fix_table()
