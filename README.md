##  🌌 Lumen: A Modern Django Social Media Platform

<p  align="center">
    <img  src="https://img.shields.io/badge/Python-3.13.7-blue?logo=python&logoColor=white" />
    <img  src="https://img.shields.io/badge/Django-5.2.5-06402B?logo=django&logoColor=white" />
    <img  src="https://img.shields.io/badge/Bootstrap-5.3.6-7952B3?logo=bootstrap&logoColor=white" />
    <img  src="https://img.shields.io/badge/HTMX-2.0.7-7952B3?logo=htmx&logoColor=white" />
    <img  src="https://img.shields.io/badge/JavaScript-BA8E23?logo=javascript&logoColor=white" />
    <img  src="https://img.shields.io/badge/Django%20Channels-4.3.1-ff6600?logo=django&logoColor=white" />
    <img  src="https://img.shields.io/badge/Django Rest Framework%20-3.16.1-red?logo=django&logoColor=white" />
</p>

---

##  📖 Overview

**Lumen** is a full-stack Django web application designed as a modern social media platform, drawing inspiration from Instagram. It delivers a seamless, interactive user experience through real-time features powered by HTMX and Django Channels. Key highlights include instant messaging, ephemeral stories, and personalized content curation, all presented in a responsive Bootstrap 5 interface.
This project emphasizes scalability, security, and developer-friendly extensibility, with a comprehensive REST API for third-party integrations.

## ✨ Core Features

###  👤 User Management

- Secure user registration, login, and profile editing (including bio, website, and avatar uploads).
- Social authentication integrations with **Google** and **GitHub**.
- Public profile viewing, including posts, followers, and following lists.

---

###  📸 Content Creation

- Public profile viewing, including posts, followers, and following lists.
- Explore page for discovering new content.
- Basic search functionality for posts and user profiles.

---

###  💬 Engagement Tools

- Real-time like/unlike actions with HTMX-driven updates.
- Post saving to private collection.
- Nested commenting system supporting up to 5 levels of replies.

---

###  💭 Real-Time Messaging

- Instant one-on-one chats using **Django Channels** and **Daphne**.
- Live typing indicators and user presence status (online/offline).
- Seamless sharing of posts and stories directly within conversations.

---

###  🎞️ Stories & Collections

- Create 24-hour ephemeral stories with images or videos.
- Story replies and in-chat sharing capabilities.
- Persistent collections for archiving stories and posts on user profiles.
- Interactive story viewer with progress bars, auto-advance, and responsive design.

---

## 🔌 RESTful API

Lumen provides a robust REST API built with **Django REST Framework**, enabling easy integration for mobile apps, SPAs, or external services. All endpoints are secured via **JWT token authentication**.

The API supports:

### ✅ Authentication & Security

- **JWT-based** token authentication for stateless sessions.
- Permission-based access.
- Secure actions.

### 👤 Profiles API

- Fetch public user profiles.
- Follow/unfollow users.
- View followers and following lists.
- Get authenticated user’s profile.

### 📸 Posts API

- Create, edit, and delete posts.
- Upload media (images/videos).
- Like / Unlike / Save posts.
- Personalized feed, saved posts.

### 💬 Comments API

- Nested comments up to 5 levels.
- Create comments or replies.
- List comments for a post.
- View full comment trees with children.

### 📚 Stories API

- Create stories (image or video).
- Stories automatically expire after 24 hours.
- View stories from users you follow.
- View stories for a specific user.
- Save a story to a collection.
- Get your own stories separately.

### 🗂 Collections API

- Create personal collections to organize saved stories and posts.
- Add or remove stories from collections.
- List all collections for a specific user.
- Private: only the owner can modify their collections.


---

##  🛠️ Tech Stack

-  **Backend:** Python 3.13.7
-  **Framework:** Django 5.2.5
-  **API:** Django REST Framework 3.16.1 
-  **Frontend:** Bootstrap 5.3.6, htmx 2.0.7, JavaScript
-  **Realtime:** Django Channels + Daphne
-  **Auth:** Django built-in system with Social Auth
-  **Media Handling:** Pillow for image compression/resizing
-  **Database:** SQLite (dev) / PostgreSQL (prod)

---

##  🚀 Setup & Installation


```bash

# Clone the repository

git  clone  https://github.com/deviantcoder/lumen.git

cd  lumen

# Create a virtual environment

python  -m  venv  venv

source  venv/bin/activate

# Install dependencies

pip  install  -r  requirements.txt

# Run migrations

python  manage.py  migrate

# Start development server

python  manage.py  runserver