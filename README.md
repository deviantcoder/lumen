##  🌌 Lumen — Django Social Media Application

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

##  📖 About

**Lumen** is a full-stack Django web application inspired by Instagram — built for modern social interaction.
It provides a dynamic, interactive experience powered by **HTMX** and **Django Channels**, featuring real-time chat, stories, and collections — all wrapped in a clean Bootstrap 5 UI.

##  ✨ Features

###  👤 User Accounts & Profiles

- Sign up, log in, and edit profiles (bio, website, avatar)
- Social authentication via **Google** and **GitHub**
- View other users’ profiles
- See user posts, followers and following

---

###  📸 Posts

- Upload **images and/or videos**
- Add captions and tags
- Discover new content via the **explore page**
- Basic **search** for posts and profiles
- Personalized **feed** for logged-in users

---

###  💬 Interactions

- Like / Unlike posts (HTMX-powered real-time updates)
- Save posts to personal collections
- Nested comments (up to 5 levels deep)

---

###  💭 Real-Time Chat

-  **Instant messaging** with **Django Channels** and **Daphne**
- Typing indicators and online/offline user status
- Integrated post & story sharing directly into chat

---

###  🎞️ Stories & Collections

- Create temporary **stories** (images or videos)
- Reply to stories or share them in chats
- Organize stories into **collections** that stay on the profile
- Responsive story viewer with progress tracking and auto-switch

---

## 🔌 REST API (Django Rest Framework)

Lumen exposes a full REST API for building clients, mobile apps, or integrating external services.

The API supports:

### ✅ Authentication & Security

- Token-based authentication using **JWT**
- Permission-based access
- Secure actions

### 👤 Profiles API

- Fetch public user profiles
- Follow/unfollow users
- View followers and following lists
- Get authenticated user’s profile

### 📸 Posts API

- Create, edit, and delete posts
- Upload media (images/videos)
- Like / Unlike / Save posts
- Personalized feed, saved posts

### 💬 Comments API

- Nested comments up to 5 levels
- Create comments or replies
- List comments for a post
- View full comment trees with children

---

##  🛠️ Tech Stack

-  **Backend:** Django 5.2.5, Python 3.13.7
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