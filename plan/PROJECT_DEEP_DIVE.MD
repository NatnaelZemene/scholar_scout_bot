# Scholarship Bot Deep Dive (Vibe Coder Guide)

## 1. Big Picture

This project is a scholarship discovery platform with four main runtime parts:

1. FastAPI backend (`app/api`) that exposes REST endpoints.
2. PostgreSQL database accessed with async SQLAlchemy (`app/db`).
3. Scraper + jobs (`app/scrapers`, `app/jobs`) that ingest and process data.
4. Telegram bot (`app/bot`) as chat UX for users.

The architecture follows layered boundaries:

- API Layer: HTTP concerns only.
- Domain Layer: business logic and validation models.
- Data Layer: ORM models and repository data access.
- Integrations: bot, scraper, background jobs.

Core philosophy implemented in code:

- API routers are thin.
- Services contain decision logic.
- Repositories isolate SQLAlchemy usage.
- Models and schema objects are separated (ORM vs Pydantic).

---

## 2. End-to-End Request Lifecycle

Example flow for `PUT /users/{telegram_id}/filters`:

1. Request enters FastAPI router in `app/api/routers/filter_router.py`.
2. Pydantic validates payload with `UserFilterUpsert` in `app/domain/schemas/filter.py`.
3. Router creates `FilterService` with `UserRepository` + `UserFilterRepository`.
4. Service checks user existence by `telegram_id`.
5. Service converts list fields to CSV with `list_to_csv` helper.
6. Repository performs upsert into `user_filters`.
7. Service converts CSV back to lists via `csv_to_list` for response shape.
8. Router commits transaction and returns `UserFilterOut`.
9. If user is missing, `NotFoundError` bubbles up.
10. Global exception handler in `app/api/main.py` returns standardized 404 JSON.

Same pattern is used by all major endpoints.

---

## 3. Folder-by-Folder Breakdown

## 3.1 Root Files

### `requirements.txt`
Pinned dependencies include:

- API/runtime: `fastapi`, `uvicorn`, `starlette`.
- Validation/config: `pydantic`, `pydantic-settings`.
- DB: `SQLAlchemy`, `asyncpg`, `alembic`.
- Bot/integrations: `python-telegram-bot`, `httpx`, `beautifulsoup4`.
- Scheduling/testing: `APScheduler`, `pytest`.

### `.env.example`
Defines required environment variables:

- `APP_NAME`
- `ENVIRONMENT`
- `VERSION`
- `DATABASE_URL`
- `API_BASE_URL`
- `TELEGRAM_BOT_TOKEN`

### `docker-compose.yml`
Creates two services:

- `db`: Postgres 16 with persisted volume.
- `api`: Python image that installs requirements, runs `alembic upgrade head`, then launches Uvicorn.

Also includes API healthcheck probing `/health`.

### `README.md`
Quickstart, route list, run commands, and troubleshooting.

### `alembic.ini`
Alembic config:

- `script_location = alembic`.
- DB URL default points to local Postgres.
- Basic logger sections configured.

---

## 3.2 Migration Layer (`alembic/`)

### `alembic/env.py`
Key behavior:

- Loads app settings from `app.core.config.settings`.
- Converts async URL to sync for Alembic by removing `+asyncpg`.
- Uses `Base.metadata` for schema autoload.
- Supports both offline and online migration modes.

### `alembic/versions/0001_initial_schema.py`
Creates tables in this order:

1. `users`
2. `scholarship_sources`
3. `user_filters`
4. `scholarships`
5. `notifications_log`

Important constraints:

- `users.telegram_id` is unique.
- `user_filters.user_id` is unique (one filter row per user).
- `scholarships.url` is unique.
- `scholarships` has unique pair `(source_id, external_id)` for upsert behavior.
- FKs include cascade for dependent cleanup.

`downgrade()` drops in reverse dependency order.

---

## 3.3 Configuration and Startup (`app/core`, root scripts)

### `app/core/config.py`
`Settings` extends `BaseSettings`, auto-loading `.env` values.

Fields:

- `app_name`
- `environment`
- `version`
- `database_url`

This is single source of truth for runtime settings used by API and DB layers.

### `app/check_settings.py`
Simple sanity script printing loaded settings, useful to validate `.env` wiring.

### `app/smoke_test.py`
Full smoke test script:

- `check_api()` validates `/health` and `/ping`.
- `check_db()` runs `SELECT 1` asynchronously.
- Adds project root to `sys.path` to avoid import errors when executed as a script.

### `app/db/smoke_test.py`
DB-only connectivity script with same import path hardening.

---

## 3.4 API Layer (`app/api`)

### `app/api/main.py`
Creates FastAPI app and registers:

- title/version from config.
- aggregate router from `app/api/routers/router.py`.
- health endpoints.
- global exception handlers.

Error response format is standardized with `_error_response()`:

```json
{
  "detail": "...",
  "code": "not_found|conflict|validation_error|internal_error",
  "path": "/request/path"
}
```

Mapped handlers:

- `NotFoundError` -> 404
- `ConflictError` -> 409
- `RequestValidationError` -> 422
- generic `Exception` -> 500

### `app/api/dependencies.py`
Exposes `db_session_dependency()` to inject async SQLAlchemy session into routers.

### `app/api/routers/router.py`
Composes domain routers:

- user router
- filter router
- scholarship router
- notification router

### `app/api/routers/user_router.py`
Endpoints:

- `POST /users` create user
- `GET /users/{telegram_id}` fetch user
- `PATCH /users/{telegram_id}` update user

Pattern:

- instantiate service in handler
- call method
- commit only on writes
- return validated response model

### `app/api/routers/filter_router.py`
Endpoints:

- `PUT /users/{telegram_id}/filters` upsert filter
- `GET /users/{telegram_id}/filters` read filter

### `app/api/routers/scholarship_router.py`
Endpoints:

- `GET /scholarships` paginated list (`skip`, `limit`)
- `GET /scholarships/search` filtering by country/level/field/deadline
- `GET /scholarships/{id}` details

### `app/api/routers/notification_router.py`
Endpoints:

- `GET /notifications/preview/{telegram_id}` compute candidate matches
- `POST /notifications/log` persist notification log row

---

## 3.5 Domain Schemas (`app/domain/schemas`)

These are Pydantic models for request/response contracts.

### `user.py`

- `UserCreate`: create payload with `telegram_id >= 1`.
- `UserUpdate`: partial updates.
- `UserOut`: full API response, includes timestamps and DB id.

`model_config = {"from_attributes": True}` allows creating from ORM objects.

### `filter.py`

- `UserFilterUpsert` input model.
- `UserFilterOut` output model.

Validation rules:

- `deadline_within_days` must be `1..365`.
- `preferred_levels` normalized to lowercase and validated against:
  - `bachelor`, `master`, `phd`, `postdoc`, `diploma`, `certificate`
- `funding_type` normalized and validated against:
  - `full`, `partial`, `tuition`, `stipend`, `mixed`

### `scholarship.py`

- `ScholarshipCreate` payload shape for insertion.
- `ScholarshipOut` API output.
- `ScholarshipSearchParams` holds query semantics (currently helper type, not directly used in router function signatures).

### `notification.py`

- `NotificationLogCreate`: log write payload.
- `NotificationLogOut`: log row response.
- `NotificationPreviewItem`, `NotificationPreviewOut`: preview structure for user matches.

### `common.py`
Utility message and error schema types (`ApiError`, `MessageOut`) for possible future reuse.

---

## 3.6 Domain Services (`app/domain/services`)

Services are framework-agnostic orchestrators.

### `exceptions.py`
Domain-level exceptions:

- `NotFoundError`
- `ConflictError`

These are intentionally generic and translated to HTTP in API layer.

### `helpers.py`
CSV/list conversion helpers:

- `list_to_csv()` for storing filter list fields into text columns.
- `csv_to_list()` for restoring API-friendly arrays.

### `user_service.py`
Responsibilities:

- `register()`: checks duplicates, raises `ConflictError` if existing telegram id.
- `get()`: fetches by telegram id, raises `NotFoundError` if missing.
- `update()`: partial update preserving existing values for omitted fields.

### `filter_service.py`
Responsibilities:

- Ensure user exists before filter operations.
- `upsert_user_filter()`: convert list fields to CSV and delegate to repository upsert.
- `get_user_filter()`: convert DB CSV fields back to list output.

### `scholarship_service.py`
Responsibilities:

- list active scholarships
- search active scholarships with filters
- fetch detail by id with not-found handling

### `notification_service.py`
Responsibilities:

- verify user and filter before preview.
- map repository match result into preview DTOs.
- create notification log by resolving `telegram_id -> user_id` first.

### `scraping_service.py`
Responsibilities:

- ensure source exists (create if missing).
- upsert each scraped scholarship by `(source_id, external_id)`.
- normalize scraper DTO into repository payload keys.

---

## 3.7 Data Layer (`app/db`)

## 3.7.1 DB Base and Session

### `app/db/base.py`
Defines SQLAlchemy declarative `Base` and imports models so metadata is complete for Alembic.

### `app/db/session.py`
Builds async engine with `pool_pre_ping=True` for dead connection resilience.

Exports:

- `engine`
- `SessionLocal` (async session factory)
- `get_db_session()` dependency generator

## 3.7.2 ORM Models (`app/db/models`)

### `user.py`
Table: `users`

Columns:

- `id` PK
- `telegram_id` unique
- optional profile fields
- timestamps

Relationships:

- one-to-one `user_filter`
- one-to-many `notifications`

### `user_filter.py`
Table: `user_filters`

- `user_id` unique FK => one filter row per user.
- preference columns stored as `Text` CSV for multi-value categories.
- `is_active` toggles participation in notifications.

### `scholarship_source.py`
Table: `scholarship_sources`

- unique source name
- source base URL
- active flag
- `last_scraped_at` for scraper health observability

### `scholarship.py`
Table: `scholarships`

Important fields:

- source mapping (`source_id`, `external_id`)
- identifying fields (`title`, unique `url`)
- filtering fields (country, level, field_of_study, funding_type, language)
- deadline and descriptive fields
- active flag

Unique business key for upsert: `(source_id, external_id)`.

### `notification_log.py`
Table: `notifications_log`

Stores send attempts/events:

- `notification_type`
- `status`
- `error_message`
- `sent_at`

FK links to user and scholarship.

## 3.7.3 Repositories (`app/db/repositories`)

### `base.py`
Stores shared async session in constructor.

### `user_repository.py`
Methods:

- `get_by_telegram_id`
- `create`
- `update`

### `user_filter_repository.py`
Methods:

- `get_by_user_id`
- `upsert` (insert if missing else update)

### `scholarship_repository.py`
Methods:

- `get_by_id`
- `get_by_source_external`
- `upsert` by source + external id
- `list` active rows with offset/limit
- `search` active rows with optional filters + pagination

### `notification_repository.py`
Methods:

- `create_log`
- `preview_matches`

`preview_matches` logic details:

1. starts with active scholarships only.
2. applies direct filters:
   - funding type (ILIKE)
   - language (ILIKE)
   - deadline window if user provided `deadline_within_days`
3. applies grouped preference logic:
   - OR within each category (levels/fields/countries)
   - AND across categories
4. limits result to 50.

### `scholarship_source_repository.py`
Methods:

- `get_by_name`
- `create`
- `update_last_scraped` timestamp (UTC now)

---

## 3.8 Scraper Layer (`app/scrapers`)

### `base.py`
Defines:

- `ScrapedScholarship` dataclass (normalized data contract).
- `BaseScholarshipScraper` abstract class with `fetch()`.

### `sources/sample_source.py`
Placeholder implementation returning one static sample scholarship.

### `runner.py`
Runtime sequence:

1. instantiate sample scraper.
2. fetch normalized records.
3. open async DB session.
4. call `ScrapingService.upsert_batch()`.
5. update source `last_scraped_at`.
6. commit.
7. print summary or error.

This is currently safe scaffolding for replacing with real parsers.

---

## 3.9 Background Jobs (`app/jobs`)

### `notification_job.py`
Main function: `run_notification_job(dry_run=True)`.

Flow:

1. query all users.
2. load each user filter.
3. skip missing/inactive filters.
4. compute matches.
5. print match counts.
6. if not dry-run, create notification log rows.

Retry behavior:

- `with_retry(action, attempts=3, delay=0.5)` wraps log writes.
- catches transient exceptions and retries.

### `cleanup_job.py`
Main function: `run_cleanup_job(notification_retention_days=90)`.

Deletes:

- notification logs older than retention cutoff.
- scholarships with passed deadlines.

### `scheduler.py`
Uses `BlockingScheduler` with wrappers that call async jobs via `asyncio.run`.

Schedules:

- notification job every 30 minutes.
- cleanup job daily at 02:00.

---

## 3.10 Telegram Bot (`app/bot`)

### `client/api_client.py`
`BackendApiClient` wraps backend HTTP calls with `httpx.AsyncClient`.

Methods:

- `health()`
- `latest_scholarships(limit=5)`

### `main.py`
Registers command handlers:

- `/start`
- `/help`
- `/filters`
- `/latest`

Behavior highlights:

- reads `TELEGRAM_BOT_TOKEN` from env and fails fast if missing.
- `/latest` calls backend and handles failure gracefully.
- fallback message shown when backend unavailable.

Current scope:

- user creation/filter update via bot is not fully wired yet.
- bot currently demonstrates read path and command skeletons.

---

## 3.11 Tests (`tests/`)

### `tests/test_health.py`
Covers:

- `GET /health` returns status ok.
- `GET /ping` returns pong.

Current test profile is minimal smoke-level API readiness.

---

## 4. Data Model and Relationships

Tables and cardinalities:

- `users` 1 -> 1 `user_filters`
- `users` 1 -> N `notifications_log`
- `scholarship_sources` 1 -> N `scholarships`
- `scholarships` 1 -> N `notifications_log`

Business keys:

- user identity key: `telegram_id`
- scholarship dedupe key: `(source_id, external_id)` and also unique `url`

---

## 5. API Contract Summary

Health:

- `GET /health`
- `GET /ping`

User:

- `POST /users`
- `GET /users/{telegram_id}`
- `PATCH /users/{telegram_id}`

Filter:

- `PUT /users/{telegram_id}/filters`
- `GET /users/{telegram_id}/filters`

Scholarship:

- `GET /scholarships?skip=0&limit=20`
- `GET /scholarships/search?country=&level=&field_of_study=&deadline_before=`
- `GET /scholarships/{id}`

Notification:

- `GET /notifications/preview/{telegram_id}`
- `POST /notifications/log`

Error behavior:

- 404 for missing resources
- 409 for conflicts
- 422 for validation errors
- 500 fallback for unhandled exceptions

---

## 6. Runtime Commands and Practical Dev Flow

Recommended daily flow:

1. Activate venv.
2. Check settings: `python -m app.check_settings`.
3. Start DB (local or docker).
4. Apply migration: `alembic upgrade head`.
5. Run API: `uvicorn app.api.main:app --reload`.
6. Optional scraper: `python -m app.scrapers.runner`.
7. Optional jobs: `python -m app.jobs.notification_job`.
8. Run tests: `pytest -q`.

---

## 7. Current Gaps and Known Realities

This section is intentionally honest so you know exactly what is scaffolded vs production-complete.

1. A real website scraper implementation is not yet plugged in (`sample_source` is static sample data).
2. Bot command `/filters` currently replies with placeholder text and does not yet call backend write endpoints.
3. Test coverage is very small (health checks only).
4. DB smoke test can fail if local Postgres credentials or DB are not provisioned exactly as `DATABASE_URL` expects.
5. Observability is basic (print statements, no structured logs/metrics stack).

---

## 8. Suggested Next Technical Expansions

If you want to take this from solid scaffold to production-ready:

1. Add service and repository unit/integration tests.
2. Add API tests for user/filter/scholarship/notification endpoints.
3. Implement real scrapers in `app/scrapers/sources/` with robust parsers.
4. Add idempotent notification sending strategy (avoid duplicate send logs).
5. Add auth/admin protection for notification logging and scraper triggers.
6. Add structured logging (JSON logs), request IDs, and metrics.
7. Introduce CI (lint, tests, migrations check).

---

## 9. Quick Mental Model

When coding new features in this repo, think in this order:

1. Define/adjust schema model in `app/domain/schemas`.
2. Add or update repository methods for persistence behavior.
3. Add service orchestration logic in `app/domain/services`.
4. Expose API endpoint in `app/api/routers`.
5. Add tests and update docs.

If a handler starts doing business logic directly, move that logic back into services.

---

## 10. Final Notes for Vibe Coding in This Project

- Build small vertical slices: schema -> service -> repo -> router -> test.
- Keep write endpoints explicit about commit boundaries.
- Keep transformation helpers (CSV/list) centralized to avoid drift.
- Keep scraper outputs normalized before touching DB layer.
- Keep bot isolated from DB; treat backend as single source of truth.

This keeps the codebase clean, explainable, and easy to scale.
