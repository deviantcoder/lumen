##  🌌 Lumen: A Modern Django Social Media Platform

<p  align="center">
    <img  src="https://img.shields.io/badge/Python-3.13.7-blue?logo=python&logoColor=white" />
    <img  src="https://img.shields.io/badge/Django-5.2.5-06402B?logo=django&logoColor=white" />
    <img  src="https://img.shields.io/badge/Bootstrap-5.3.6-7952B3?logo=bootstrap&logoColor=white" />
    <img  src="https://img.shields.io/badge/HTMX-2.0.7-7952B3?logo=htmx&logoColor=white" />
    <img  src="https://img.shields.io/badge/JavaScript-BA8E23?logo=javascript&logoColor=white" />
    <img  src="https://img.shields.io/badge/Django%20Channels-4.3.1-ff6600?logo=django&logoColor=white" />
    <img  src="https://img.shields.io/badge/Django Rest Framework%20-3.16.1-red?logo=django&logoColor=white" />
    <img  src="https://img.shields.io/badge/Celery-5.5.3-cyan?logo=celery&logoColor=white" />
    <img  src="https://img.shields.io/badge/RabbitMQ-4.2.0-orange?logo=rabbitmq&logoColor=white" />
    <img  src="https://img.shields.io/badge/Redis-8.4.0-red?logo=redis&logoColor=white" />
    <img  src="https://img.shields.io/badge/Docker-28.5.2-blue?logo=docker&logoColor=white" />
    <img  src="https://img.shields.io/badge/SQLite-dev-cyan?logo=sqlite&logoColor=white" />
    <img  src="https://img.shields.io/badge/Elasticsearch-9.2.1-blue?logo=elasticsearch&logoColor=white" />
    <img  src="https://img.shields.io/badge/PostgreSQL-18-blue?logo=postgresql&logoColor=white" />
</p>

---

##  📖 Overview

**Lumen** is a full-stack Django web application designed as a modern social media platform, drawing inspiration from Instagram. It delivers a seamless, interactive user experience through real-time features powered by HTMX and Django Channels. Key highlights include instant messaging, ephemeral stories, and personalized content curation, all presented in a responsive Bootstrap 5 interface.
This project emphasizes scalability, security, and developer-friendly extensibility, with a comprehensive REST API for third-party integrations.

## ✨ Core Features

- **Modern Social Experience**  
  Instagram-inspired feed, stories, likes, nested comments (up to 5 levels), saves/collections, and an Explore page with search.

- **User Profiles & Auth**  
  Customizable profiles (avatar, bio, website), follow system, **Google** & **GitHub** social login.

- **Real-Time Interaction**  
  Instant private messaging with typing indicators and online status via **Django Channels**.  
  Live like/unlike and comment loading powered by **HTMX**.

- **Ephemeral Stories**  
  24-hour stories (image/video) with replies, highlights/collections, and beautiful full-screen viewer.

- **Performance & Scalability**  
  Infinite scroll pagination (posts, comments, feeds), **Redis** caching, advanced filtering by **django-filter**, background tasks with **Celery + RabbitMQ** (image processing, email, cleanup).

- **Robust REST API** (Django REST Framework)  
  Full JWT-secured API for posts, comments, stories, profiles, messaging, and collections — ready for mobile or SPA clients.

---

## 🔌 RESTful API

Lumen provides a fully featured REST API built with **Django REST Framework**, enabling easy integration for mobile apps, SPAs, or external services. All endpoints are secured with **JWT token authentication**.

Main endpoints include:

- **✅ Auth**: JWT login, signup, permissions.
- **👤 Profiles**: View profiles, follow/unfollow, followers/following.
- **📸 Posts**: Create/edit/delete posts, media upload, likes, saved posts, personalized feed.
- **💬 Comments**: Nested comments, replies, full comment trees.
- **📚 Stories**: 24h stories, view by user or following, save to collections.
- **🗂 Collections**: Organize stories into private collections.

---

##  🛠️ Tech Stack

-  **Backend:** Python 3.13.7, Django 5.2.5, Daphne 4.2.1
-  **API:** Django REST Framework 3.16.1 
-  **Async Tasks:** Celery 5.5.3, RabbitMQ 4.2.0
-  **Caching**: Redis 8.4.0
-  **Frontend:** Bootstrap 5.3.6, htmx 2.0.7, JavaScript
-  **Realtime:** Django Channels + Daphne
-  **Auth:** Django built-in auth + Social Auth
-  **Media Handling:** Pillow
-  **Database:** SQLite (dev) / PostgreSQL (prod)
-  **Containerization**: Docker

---

##  🚀 Setup & Installation


```bash

# Clone the repository
git clone https://github.com/deviantcoder/lumen.git
cd lumen

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development servers

# Terminal 1: Django + Daphne
python manage.py runserver

# Terminal 2: Celery worker
celery -A core worker -l INFO

# Terminal 3 (optional for dev): Redis (if not using Docker)
docker compose up -d