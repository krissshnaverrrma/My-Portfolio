import os
from dotenv import load_dotenv
load_dotenv()


class LinkedInPortfolio:
    def __init__(self):
        self.username = os.getenv("LINKEDIN_USER", "krishna-verma-43aa85315")
        self.profile_url = f"https://www.linkedin.com/in/{self.username}"
        self.profile = {
            "name": "Krishna Verma",
            "headline": "CS Student | Python & Backend Developer",
            "location": "Hapur, Uttar Pradesh, India",
            "about": (
                "Computer Science undergraduate passionate about building scalable backend systems "
                "using Python. Interested in Game Development, Data Structures, and automating "
                "daily tasks through code."
            ),
            "avatar_url": "",
            "profile_url": self.profile_url
        }
        self.experience = [
            {
                "role": "Computer Science Student",
                "company": "SCET",
                "duration": "2024 - Present",
                "description": "Focusing on Data Structures, Algorithms (C++/Python), and Web Technologies."
            }
        ]
        self.certifications = [
            "Python (Basic) - HackerRank",
            "Problem Solving (Intermediate) - HackerRank"
        ]

    def get_profile(self):
        """Returns the main profile dictionary."""
        return self.profile

    def get_experience(self):
        """Returns the list of experience/education."""
        return self.experience

    def get_certifications(self):
        """Returns list of certifications."""
        return self.certifications


if __name__ == "__main__":
    li = LinkedInPortfolio()
    print(f"--- LinkedIn Data for {li.get_profile()['name']} ---")
    print(f"Headline: {li.get_profile()['headline']}")
    print(f"URL: {li.get_profile()['profile_url']}")
    print("\n--- Experience ---")
    for job in li.get_experience():
        print(f"* {job['role']} at {job['company']} ({job['duration']})")
