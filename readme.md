# 🚀 Krishna Verma's Portfolio & Virtual AI Assistant

A high-performance personal portfolio featuring an intelligent Virtual Assistant powered by a custom multi-model fallback architecture and a modern glassmorphic "Push" layout.

---
## My-Portfolio-Review

![My-Portfolio](/static/assets/my_portfolio_preview.png)

## ✨ Key Features

### 🧠 Smart AI Assistant (Gemini Multi-Model Stack)
- **Zero-Downtime Architecture**: The assistant is built with a sophisticated fallback system. It prioritizes the high-reasoning **Gemini 2.5 Flash**, but automatically rotates to **2.0 Flash-Lite** or **1.5 Flash** if API quotas are reached.
- **Contextual Intelligence**: Fully integrated with personal data sources including GitHub repositories, LinkedIn history, and a custom knowledge base for accurate, real-time answers.
- **Auto-Status Detection**: Features a live status indicator (Online/Sleeping) that reacts instantly to API availability and rate limits.

### 🎨 Premium UI/UX Design
- **Dynamic Push Layout**: Unlike traditional overlays, the chat window uses a Flexbox "Push" mechanism. When toggled, the main portfolio content smoothly compresses to the left, allowing users to browse projects and chat simultaneously.
- **Glassmorphic Aesthetic**: Deep blurs, semi-transparent panels, and high-fidelity CSS transitions for a premium, futuristic feel.
- **Responsive Fluidity**: Seamlessly transitions from a desktop side-panel to a mobile-optimized overlay.

---

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS , JavaScript , Bootstrap.
- **Backend**: Python (Flask).
- **AI Integration**: Google Generative AI (Gemini API), Custom Fallback Logic.
- **Database/Storage**: Integrated Knowledge Base for Portfolio-Specific Context with Render INTERNAL and EXTERNAL URL .

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- A Google AI Studio (Gemini) API Key

### 2. Installation
```bash
# Clone the repository
git clone [https://github.com/krissshnaverrrma/My-Portfolio.git](https://github.com/krissshnaverrrma/My-Portfolio.git)

# Install dependencies
pip install -r requirements.txt
3. Environment Setup
Create a .env file in the root directory and add your credentials:

Code snippet
# API Keys
GEMINI_API_KEY=your_actual_key_here

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=a_random_long_string_for_session_security

# Optional: Portfolio Context Data
GITHUB_USERNAME=your_github_username
LINKEDIN_URL=your_linkedin_profile_url

4. Run the App
Bash

python app.py

⚙️ The Fallback Logic
To ensure a 100% free yet reliable experience, the bot handles the 429 Quota Exceeded error gracefully:

Primary: Gemini 2.5 Flash (Best Reasoning)

Secondary: Gemini 2.0 Flash-Lite (Highest Speed/Limit)

Tertiary: Gemini 1.5 Flash (Reliable Backup)

The system catches the rate limit exception and switches the "AI Brain" instantly, ensuring the visitor never sees a broken interface.
```

🌐 Deployment
Optimized for deployment on Render.
```
Build Command: pip install -r requirements.txt
```

Start Command: gunicorn app:app

Developed with ❤️ by Krishna Verma - Lazy Coder 