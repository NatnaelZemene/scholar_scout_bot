# Scholarship Bot Project TODO (Step-by-Step)

## 0) Ground Rules

- [ ] Keep architecture aligned with `plan/ARCHITECTURE.MD`.
- [ ] Work in small commits by phase (after each section below).
- [ ] Run `get_errors` / lint checks before closing each phase.

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
- [ ] Add migration strategy (Alembic preferred).
- [ ] Generate first migration for all current models.
- [ ] Apply migration to local DB.

### DB model checks

- [ ] `users`
- [ ] `user_filters`
- [ ] `scholarship_sources`
- [ ] `scholarships`
- [ ] `notifications_log`

---

## 3) API Foundation

- [ ] Keep health endpoints stable (`/health`, `/ping`).
- [ ] Split placeholder router into domain routers:
  - [ ] `user_router`
  - [ ] `filter_router`
  - [ ] `scholarship_router`
  - [ ] `notification_router`
- [ ] Add request/response schemas for each router.
- [ ] Standardize error responses (404, 409, 422, 500).
- [ ] Add API tags and route prefixes consistently.

---

## 4) Repository Layer (Data Access)

- [ ] Create `app/db/repositories/` package.
- [ ] Add `base.py` for shared DB utilities.
- [ ] Implement `user_repository.py`.
- [ ] Implement `user_filter_repository.py`.
- [ ] Implement `scholarship_repository.py`.
- [ ] Implement `notification_repository.py`.
- [ ] Implement `scholarship_source_repository.py`.
- [ ] Ensure no raw SQL is used in API handlers.

---

## 5) Service Layer (Business Logic)

- [ ] Create `app/domain/services/` package.
- [ ] Implement `UserService`:
  - [ ] register/get/update user
- [ ] Implement `FilterService`:
  - [ ] create/update user filter
- [ ] Implement `ScholarshipService`:
  - [ ] list/search scholarships with filters
- [ ] Implement `NotificationService`:
  - [ ] compute eligible recipients for scholarship updates
- [ ] Keep services framework-agnostic (no FastAPI objects inside).

---

## 6) Feature Completion (Core MVP)

### User Management

- [ ] `POST /users` create/register user.
- [ ] `GET /users/{telegram_id}` fetch user.
- [ ] `PATCH /users/{telegram_id}` update profile.

### Filter Management

- [ ] `PUT /users/{telegram_id}/filters` create/update filter.
- [ ] `GET /users/{telegram_id}/filters` read filter.
- [ ] Validate allowed values (levels, funding_type, etc.).

### Scholarships

- [ ] `GET /scholarships` list with pagination.
- [ ] `GET /scholarships/search` query by country/level/field/deadline.
- [ ] `GET /scholarships/{id}` details endpoint.

### Notifications

- [ ] API endpoint to preview matches per user.
- [ ] API endpoint to log sent notifications.

---

## 7) Scraper Integration (Incremental)

- [ ] Create scraper base interface (`app/scrapers/base.py`).
- [ ] Add 1 real source implementation first.
- [ ] Normalize scraped fields to scholarship schema.
- [ ] Upsert by `(source_id, external_id)`.
- [ ] Add source health/error logging.
- [ ] Add runner command for manual scraping.

---

## 8) Background Jobs

- [ ] Create `app/jobs/notification_job.py`.
- [ ] Create `app/jobs/cleanup_job.py`.
- [ ] Schedule periodic job (APScheduler or OS scheduler).
- [ ] Add dry-run mode for notification job.
- [ ] Add retry strategy for transient failures.

---

## 9) Telegram Bot Integration

- [ ] Set up `app/bot/main.py` with token config.
- [ ] Add handlers for:
  - [ ] `/start`
  - [ ] `/help`
  - [ ] `/filters`
  - [ ] `/latest`
- [ ] Build `api_client` for backend calls.
- [ ] Add user-friendly fallback/error messages.

---

## 10) Quality & Testing

- [ ] Add tests folder structure if not present.
- [ ] Add unit tests for services.
- [ ] Add repository integration tests (test DB).
- [ ] Add API tests for critical routes.
- [ ] Add smoke test script for app startup + DB + key route.
- [ ] Ensure all tests pass before merge.

---

## 11) Docs & Developer Experience

- [ ] Create `README.md` with:
  - [ ] setup steps
  - [ ] env variables
  - [ ] run commands
  - [ ] API quick examples
- [ ] Add `.env.example`.
- [ ] Document project structure and conventions.
- [ ] Add troubleshooting section (DB connection, import issues, migrations).

---

## 12) Deployment Readiness

- [ ] Add `docker-compose.yml` (API + Postgres).
- [ ] Add healthcheck for API container.
- [ ] Configure production env vars.
- [ ] Add migration execution on deployment.
- [ ] Add logging and monitoring baseline.

---

## 13) Definition of Done (Project Finish)

- [ ] API runs locally without errors.
- [ ] DB schema created and migrations tracked.
- [ ] Core endpoints for users/filters/scholarships working.
- [ ] Scraper imports data into DB.
- [ ] Notification matching flow works end-to-end.
- [ ] Telegram bot can read/update filters and fetch scholarships.
- [ ] Tests and smoke checks pass.
- [ ] README and `.env.example` are complete.
