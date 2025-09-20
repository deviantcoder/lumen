# 🌌 Lumen — Instagram-like Django Application

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=cyan" />
  <img src="https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white" />
  <img src="https://img.shields.io/badge/HTMX-3366cc?logo=htmx&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-3366cc?logo=javascript&logoColor=white" />
</p>

---

## 📖 About

**Lumen** is a full-stack Django web application inspired by Instagram.  
It allows users to share posts with media (images & videos), interact through likes, saves, and comments, and manage profiles — all in a smooth, modern UI powered by **HTMX** for real-time interactivity.

---

## ✨ Features

- 👤 **User accounts & profiles**  
  - Signup, login, profile editing (bio, website, avatar)
  - Social authentication (Google, Github)

- 📸 **Posts**  
  - Upload images/videos  
  - Captions and tags  
  - Post feed

- ❤️ **Interactions**  
  - Like / unlike posts (real-time with HTMX)  
  - Save posts to personal collection  
  - Comment system

- ⚡ **Modern UX**  
  - HTMX for partial page updates (no full reloads)  
  - Bootstrap 5

---

## 🛠️ Tech Stack

- **Backend**: `Django` + `Python`  
- **Frontend**: `Bootstrap 5` + `HTMX` + `JavaScript` 
- **Auth**: Django’s built-in authentication system with custom backends, social authentication
- **Media Handling**: image compression and resizing using `Pillow`
