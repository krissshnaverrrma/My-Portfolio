from database import init_db, SessionLocal, BlogPost
import datetime

init_db()
db = SessionLocal()

print("--- 🌱 Seeding Blog Posts with Images ---")

posts_data = [
    {
        "title": "The Lazy Developer Manifesto",
        "slug": "lazy-developer-manifesto",
        "summary": "Why working hard is overrated and smart engineering is the future.",
        "image_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80",
        "content": """<p>People think being a 'lazy' developer is a bad thing...</p>""" 
    },
    {
        "title": "Why Python is the Best Snake",
        "slug": "why-python-is-best",
        "summary": "Forget cobras. Python swallows complexity whole.",
        "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80",
        "content": """<p>I have tried C++. I have dabbled in Java...</p>"""
    },
    {
        "title": "The Art of Debugging",
        "slug": "art-of-debugging",
        "summary": "Six hours of debugging can save you five minutes of reading documentation.",
        "image_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80",
        "content": """<p>Debugging is the murder mystery of the coding world...</p>"""
    },
    {
        "title": "Data Structures: Why Trees Matter",
        "slug": "data-structures-trees",
        "summary": "They aren't just for climbing. Understanding the hierarchy of the web.",
        "image_url": "https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&w=800&q=80",
        "content": """<p>In CS 101, Binary Trees seem like abstract torture...</p>"""
    },
    {
        "title": "Frontend vs Backend: The Civil War",
        "slug": "frontend-vs-backend",
        "summary": "Choosing a side in the battle of pixel-perfect CSS vs scalable APIs.",
        "image_url": "https://images.unsplash.com/photo-1571171637578-41bc2dd41cd2?auto=format&fit=crop&w=800&q=80",
        "content": """<p>Every CS major faces a crossroads...</p>"""
    },
    {
        "title": "Surviving the Night Before the Exam",
        "slug": "surviving-cs-exams",
        "summary": "Caffeine, StackOverflow, and the power of last-minute panic.",
        "image_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=800&q=80",
        "content": """<p>The roadmap to a Computer Science degree...</p>"""
    }
]

for post in posts_data:
    existing = db.query(BlogPost).filter(BlogPost.slug == post['slug']).first()
    if not existing:
        new_post = BlogPost(
            title=post['title'],
            slug=post['slug'],
            summary=post['summary'],
            content=post['content'],
            image_url=post['image_url'], 
            created_at=datetime.datetime.utcnow()
        )
        db.add(new_post)
        print(f"✅ Added: {post['title']}")
    else:
        existing.image_url = post['image_url']
        print(f"🔄 Updated Image: {post['title']}")

db.commit()
db.close()
print("--- 🎉 Done! Database Created & Updated ---")
