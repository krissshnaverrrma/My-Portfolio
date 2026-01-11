import os
from dotenv import load_dotenv
from database import add_fact, get_all_knowledge
load_dotenv()
print("--- 🚀 FORCE SEEDING DATA ---")
add_fact("Contact Email", os.getenv(
    "CONTACT_EMAIL", "krishnav24-cs@sanksar.org"))
add_fact("Hobbies", os.getenv("HOBBIES", "Coding, Gaming, Sci-Fi"))
add_fact("Favorite Tech", os.getenv("FAVORITE_TECH", "Python & AI"))
print("\n✅ Done! Here is what is currently in your Cloud Database:")
print(get_all_knowledge())
