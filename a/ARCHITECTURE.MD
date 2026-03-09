## Scholarship Scout/Finder Telegram Bot – System Architecture

### 1. Overview

This project is a **Scholarship Scout/Finder Telegram Bot** targeting **Ethiopian students**. It:

- Scrapes scholarship information from selected websites.
- Stores normalized scholarship data and user preferences in **PostgreSQL**.
- Exposes a **FastAPI** backend for:
  - Managing users and their filters.
  - Serving scholarship data (for bot and future frontends).
  - Triggering or monitoring scraping.
- Uses a **Telegram bot (python-telegram-bot)** as the primary user interface.

The system is designed with **clean architecture principles** and separation of concerns so it can grow into a production-quality service.

---

### 2. High-Level Components

1. **Telegram Bot Service (python-telegram-bot)**
   - Handles all interaction with Telegram users.
   - Receives commands like `/start`, `/help`, `/filters`, `/latest`, `/admin`.
   - Communicates with the FastAPI backend via HTTP (JSON) using an internal `api_client`.
   - Does **not** talk directly to the database.

2. **Backend API Service (FastAPI)**
   - Contains the core **business logic**.
   - Provides REST endpoints for:
     - User registration & profile management.
     - Filter (preferences) management.
     - Scholarship listing & search.
     - Notification and scraping control (for admin).
   - Uses a **service layer** that orchestrates logic.
   - Uses a **repository layer** to access PostgreSQL.

3. **Database (PostgreSQL)**
   - Stores persistent data:
     - `users`: Telegram users and basic profile info.
     - `user_filters`: per-user scholarship preferences.
     - `scholarship_sources`: which sites are scraped.
     - `scholarships`: normalized scholarship records.
     - `notifications_log`: which user received which notification and when.
   - Accessed exclusively through repository classes (no raw SQL in handlers).

4. **Scraper Workers**
   - Independent scripts/services that:
     - Scrape scholarship data from target websites using `httpx` + `BeautifulSoup`.
     - Normalize the data into internal schema (country, level, field, funding type, language, deadline, amount).
     - Send new/updated scholarships to the backend (via API or directly through repositories).

5. **Background Jobs**
   - Periodic jobs responsible for:
     - Matching newly added scholarships with user filters.
     - Sending notifications about:
       - New scholarships.
       - Approaching deadlines.
     - Optional cleanup of expired scholarships and old logs.

---


### 3. Clean Architecture Layers

The backend is structured by **layers**, not by framework:

- **API Layer (`app/api`)**
  - FastAPI routers and endpoint definitions.
  - Handles HTTP details (status codes, path/query parameters, request/response models).
  - Delegates work to service layer.

- **Domain Layer (`app/domain`)**
  - **Schemas** (`app/domain/schemas`):
    - Pydantic models for:
      - Request/response bodies (UserCreate, ScholarshipOut, FilterUpdate, etc.).
      - Internal data transfer objects.
  - **Services** (`app/domain/services`):
    - Pure business logic.
    - Example services:
      - `UserService`: register/update user, fetch user by Telegram ID.
      - `ScholarshipService`: create/update scholarships, search by filters.
      - `NotificationService`: compute which scholarships to notify each user about.
      - `ScrapingService`: handle normalized scholarship input from scrapers.
    - Services call **repositories** but don’t know about HTTP.

- **Data Layer (`app/db`)**
  - **Models** (`app/db/models`):
    - SQLAlchemy ORM models for:
      - `User`, `UserFilter`, `Scholarship`, `ScholarshipSource`, `NotificationLog`.
  - **Session Management** (`app/db/session.py`):
    - Creates the async SQLAlchemy engine and session factory.
  - **Repositories** (`app/db/repositories`):
    - Encapsulate all DB access:
      - `UserRepository`, `ScholarshipRepository`, `NotificationRepository`, etc.
    - Provide high-level operations:
      - `get_user_by_telegram_id`, `update_filters`, `upsert_scholarship`, `get_matching_scholarships_for_user`, etc.

- **Presentation / Integrations**
  - **Telegram Bot (`app/bot`)**:
    - Presentation layer for Telegram:
      - Command handlers.
      - Inline keyboards.
      - Conversations.
    - Uses `api_client` to call backend.
  - **Scrapers (`app/scrapers`)**:
    - Integrate with external websites and map them into the domain model.
  - **Jobs (`app/jobs`)**:
    - Integrate with OS-level schedulers (cron, Task Scheduler) or APScheduler.

---

### 4. Project Folder Structure

```text
scholarship_bot/
  app/
    core/
      config.py
      logging_config.py
      security.py           # (optional, future auth)
    db/
      base.py
      session.py
      models/
        user.py
        scholarship.py
        notification.py
      repositories/
        base.py
        user_repository.py
        scholarship_repository.py
        notification_repository.py
    domain/
      schemas/
        user.py
        scholarship.py
        filters.py
        notification.py
      services/
        user_service.py
        scholarship_service.py
        notification_service.py
        scraping_service.py
    api/
      main.py
      dependencies.py
      routers/
        user_router.py
        scholarship_router.py
        notification_router.py
        scraping_router.py
    bot/
      config.py
      main.py
      handlers/
        start.py
        filters.py
        list_scholarships.py
        admin.py
      keyboards/
        filters.py
        common.py
      client/
        api_client.py
    scrapers/
      base.py
      sources/
        example_site.py
        another_site.py
      runner.py
      utils.py
    jobs/
      notification_job.py
      cleanup_job.py
  tests/
  alembic/
  .env.example
  requirements.txt or pyproject.toml
  docker-compose.yml
  README.md