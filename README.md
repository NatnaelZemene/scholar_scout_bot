# Scholarship Bot

FastAPI backend + Telegram bot scaffold for scholarship discovery.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` from `.env.example`.
4. Validate settings:
   ```bash
   python -m app.check_settings
   ```

## Database and Migrations

1. Start Postgres and create database `scholar_scout`.
2. Run migration:
   ```bash
   alembic upgrade head
   ```
3. Verify DB connection:
   ```bash
   python app/db/smoke_test.py
   ```

## Run API

```bash
uvicorn app.api.main:app --reload
```

Important routes:
- `GET /health`
- `POST /users`
- `GET /users/{telegram_id}`
- `PATCH /users/{telegram_id}`
- `PUT /users/{telegram_id}/filters`
- `GET /users/{telegram_id}/filters`
- `GET /scholarships`
- `GET /scholarships/search`
- `GET /scholarships/{id}`
- `GET /notifications/preview/{telegram_id}`
- `POST /notifications/log`

## Run Scraper and Jobs

```bash
python -m app.scrapers.runner
python -m app.jobs.notification_job
python -m app.jobs.cleanup_job
```

## Run Telegram Bot

Set `TELEGRAM_BOT_TOKEN` and run:

```bash
python -m app.bot.main
```

## Docker Compose

```bash
docker compose up --build
```

This starts PostgreSQL and API and applies migrations on API startup.

## Project Conventions

- API handlers stay thin and delegate to services.
- Services contain business rules and return domain objects.
- Repositories own database access.
- Keep framework-specific code out of domain services.

## Troubleshooting

- DB connection error: verify Postgres is running and `DATABASE_URL` is correct.
- Import errors: run commands from project root and ensure venv is active.
- Migration issues: check `alembic.ini` URL and run `alembic current`.
- Bot cannot fetch data: verify `API_BASE_URL` and API service health.
