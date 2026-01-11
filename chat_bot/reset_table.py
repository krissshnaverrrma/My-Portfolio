from sqlalchemy import text
from database import engine, Base, BlogPost


def reset_blog_table():
    print("--- 🧨 FORCE RESETTING BLOG TABLE ---")

    with engine.begin() as conn:
        print("🗑️ Dropping old blog_posts table...")
        conn.execute(text("DROP TABLE IF EXISTS blog_posts;"))
        print("✅ Old Table Deleted.")
        
    print("🔨 Rebuilding Table with New Columns...")
    Base.metadata.create_all(bind=engine)
    print("✅ New Table Created Successfully!")


if __name__ == "__main__":
    reset_blog_table()
