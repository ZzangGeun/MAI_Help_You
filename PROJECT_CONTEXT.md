# MAI_Help_You Project Context & Structure

## 1. Project Overview
- **Type:** Hybrid Web Application (Django Backend serving React Frontend)
- **Goal:** MapleStory Information & Chatbot Service.
- **Current State:** Fully integrated. React is built into static files, and Django serves the single entry point (`index.html`) for all non-API routes.

## 2. Tech Stack
- **Backend:** Django 5.x, Django REST Framework, Python 3.11
- **Frontend:** React 18, Vite, Styled-components (CSS files)
- **Data:** SQLite (Default), Nexon Open API (External), BeautifulSoup4 (Crawling)
- **Environment:** MacOS (Darwin)

## 3. Architecture & Integration
- **Single Server Mode:** Django runs on port `8000`.
- **Frontend Integration:**
  - React build output: `static/dist/`
  - Django Static Config: `settings.STATICFILES_DIRS` includes `BASE_DIR / 'static'`.
  - **View:** `core.views.serve_react` reads `static/dist/index.html` and serves it.
  - **URL Routing:** `maple_chatbot/urls.py` has a catch-all `re_path(r'^.*$', serve_react)` at the end.
- **API Communication:** Frontend calls `/api/...` endpoints served by Django.

## 4. Key Directory Structure
```text
/
├── manage.py           # Django Entry
├── mai_env/            # Virtual Environment
├── static/dist/        # React Build Output (index.html, assets/)
├── character_data/     # JSON Cache for API responses (Notices, Rankings)
├── maple_chatbot/      # Main Django Config (settings.py, urls.py)
├── core/               # App: Main Page Logic & Common Services
│   ├── views.py        # contains `serve_react`
│   ├── services.py     # Logic: API calls, Caching, OG Image Crawling
│   └── api/            # DRF Views for Home Data
├── character/          # App: Character Search Logic
│   ├── get_character_info.py # Nexon API Wrapper (Complex parsing)
│   └── views.py        # `/character/api/search/` endpoint
├── chat/               # App: AI Chatbot Logic
├── accounts/           # App: User Auth (Signup, Login, Profile)
└── frontend/           # React Source
    ├── vite.config.js  # Configured with base: '/static/dist/'
    ├── src/
    │   ├── pages/      # HomePage.jsx (Main Dashboard)
    │   ├── api/        # Axios clients
    │   └── styles/     # home.css (Key Layout Styles), common.css
```

## 5. Key Features & Logic

### Backend (`core/services.py`)
- **Notice Caching:** Caches API responses in `character_data/notice_data.json` for 1 hour.
- **Image Crawling:** `get_og_image` uses `BeautifulSoup` to fetch thumbnails for Notices since the API doesn't provide them. Only crawls the top item to save resources.
- **Character Data:** `character/get_character_info.py` fetches extensive data from Nexon API, including popularity (merged into `basic_info`).

### Frontend (`HomePage.jsx`)
- **One-Page Layout:** Designed to fit `100vh` without scrolling.
- **Dynamic Sidebar:**
  - **Left:** Shows "My Character" if logged in, otherwise "Search Result".
  - **Right:** Sponsored Ad (Height synchronized with main content).
- **Auto-Search:** On login (`useAuth`), automatically fetches the user's main character info.

### Styling (`home.css`)
- **Layout:** Grid system (`sidebar-left`, `main-content`, `sidebar-right`).
- **Adjustments:**
  - `.main-content`: `min-height: 350px` (Compact).
  - `.sidebar-ad-long`: `height: 100%` (Matches main content).
  - `.bottom-section`: Reduced margins to fit viewport.

## 6. User & Auth Info
- **Test User:** `testuser12345` / `password123!`
- **Profile:** Has `maple_nickname='오지환'` linked.

## 7. Operational Commands
1. **Build Frontend:** `cd frontend && npm run build`
2. **Run Server:** `cd .. && ./mai_env/bin/python manage.py runserver`
   *(Note: Always ensure you are in the root directory before running python)*

## 8. Recent Fixes
- Fixed layout to prevent scrolling (Compact height).
- Restored missing CSS for Titles (Gradient text).
- Implemented OG Image crawling for Notices.
- Implemented "My Character" auto-load on sidebar.
