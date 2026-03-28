# Scholarship Bot Project TODO (Step-by-Step)

## 0) Ground Rules

- [x] Keep architecture aligned with `plan/ARCHITECTURE.MD`.
- [ ] Work in small commits by phase (after each section below).
- [x] Run `get_errors` / lint checks before closing each phase.

---

## 1) Environment & Local Setup

- [x] Confirm Python version (recommended 3.11+).
- [x] Create virtual environment: `py -m venv .venv`.
- [x] Activate venv: `.\.venv\Scripts\Activate.ps1`.
- [x] Install dependencies: `pip install -r requirements.txt`.
- [x] Add `.env` in project root.
- [x] Verify app settings: `python -m app.check_settings`.

### Required `.env` values

- [x] `APP_NAME=Scholarship Scout Bot`
- [x] `ENVIRONMENT=dev`
- [x] `VERSION=1.0.0`
- [x] `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/scholar_scout`

---

## 2) Database Readiness

- [ ] Start PostgreSQL locally (or Docker).
- [ ] Create database: `scholar_scout`.
- [ ] Verify DB connection with `python app/db/smoke_test.py`.
- [x] Add migration strategy (Alembic preferred).
- [x] Generate first migration for all current models.
- [ ] Apply migration to local DB.

### DB model checks

- [x] `users`
- [x] `user_filters`
- [x] `scholarship_sources`
- [x] `scholarships`
- [x] `notifications_log`

---

## 3) API Foundation

- [x] Keep health endpoints stable (`/health`, `/ping`).
- [x] Split placeholder router into domain routers:
  - [x] `user_router`
  - [x] `filter_router`
  - [x] `scholarship_router`
  - [x] `notification_router`
- [x] Add request/response schemas for each router.
- [x] Standardize error responses (404, 409, 422, 500).
- [x] Add API tags and route prefixes consistently.

---

## 4) Repository Layer (Data Access)

- [x] Create `app/db/repositories/` package.
- [x] Add `base.py` for shared DB utilities.
- [x] Implement `user_repository.py`.
- [x] Implement `user_filter_repository.py`.
- [x] Implement `scholarship_repository.py`.
- [x] Implement `notification_repository.py`.
- [x] Implement `scholarship_source_repository.py`.
- [x] Ensure no raw SQL is used in API handlers.

---

## 5) Service Layer (Business Logic)

- [x] Create `app/domain/services/` package.
- [x] Implement `UserService`:
  - [x] register/get/update user
- [x] Implement `FilterService`:
  - [x] create/update user filter
- [x] Implement `ScholarshipService`:
  - [x] list/search scholarships with filters
- [x] Implement `NotificationService`:
  - [x] compute eligible recipients for scholarship updates
- [x] Keep services framework-agnostic (no FastAPI objects inside).

---

## 6) Feature Completion (Core MVP)

### User Management

- [x] `POST /users` create/register user.
- [x] `GET /users/{telegram_id}` fetch user.
- [x] `PATCH /users/{telegram_id}` update profile.

### Filter Management

- [x] `PUT /users/{telegram_id}/filters` create/update filter.
- [x] `GET /users/{telegram_id}/filters` read filter.
- [x] Validate allowed values (levels, funding_type, etc.).

### Scholarships

- [x] `GET /scholarships` list with pagination.
- [x] `GET /scholarships/search` query by country/level/field/deadline.
- [x] `GET /scholarships/{id}` details endpoint.

### Notifications

- [x] API endpoint to preview matches per user.
- [x] API endpoint to log sent notifications.

---

## 7) Scraper Integration (Incremental)

- [x] Create scraper base interface (`app/scrapers/base.py`).
- [ ] Add 1 real source implementation first.
- [x] Normalize scraped fields to scholarship schema.
- [x] Upsert by `(source_id, external_id)`.
- [x] Add source health/error logging.
- [x] Add runner command for manual scraping.

---

## 8) Background Jobs

- [x] Create `app/jobs/notification_job.py`.
- [x] Create `app/jobs/cleanup_job.py`.
- [x] Schedule periodic job (APScheduler or OS scheduler).
- [x] Add dry-run mode for notification job.
- [x] Add retry strategy for transient failures.

---

## 9) Telegram Bot Integration

- [x] Set up `app/bot/main.py` with token config.
- [x] Add handlers for:
  - [x] `/start`
  - [x] `/help`
  - [x] `/filters`
  - [x] `/latest`
- [x] Build `api_client` for backend calls.
- [x] Add user-friendly fallback/error messages.

---

## 10) Quality & Testing

- [x] Add tests folder structure if not present.
- [ ] Add unit tests for services.
- [ ] Add repository integration tests (test DB).
- [ ] Add API tests for critical routes.
- [x] Add smoke test script for app startup + DB + key route.
- [x] Ensure all tests pass before merge.

---

## 11) Docs & Developer Experience

- [x] Create `README.md` with:
  - [x] setup steps
  - [x] env variables
  - [x] run commands
  - [x] API quick examples
- [x] Add `.env.example`.
- [x] Document project structure and conventions.
- [x] Add troubleshooting section (DB connection, import issues, migrations).

---

## 12) Deployment Readiness

- [x] Add `docker-compose.yml` (API + Postgres).
- [x] Add healthcheck for API container.
- [ ] Configure production env vars.
- [x] Add migration execution on deployment.
- [ ] Add logging and monitoring baseline.

---

## 13) Definition of Done (Project Finish)

- [x] API runs locally without errors.
- [ ] DB schema created and migrations tracked.
- [x] Core endpoints for users/filters/scholarships working.
- [ ] Scraper imports data into DB.
- [ ] Notification matching flow works end-to-end.
- [ ] Telegram bot can read/update filters and fetch scholarships.
- [ ] Tests and smoke checks pass.
- [x] README and `.env.example` are complete.
