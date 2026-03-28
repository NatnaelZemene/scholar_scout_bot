# Amazing Scholar Scout Telegram Bot - Activation Todo List

This document outlines the actionable steps required to take the scaffolding of the Scholarship Bot and turn it into a fully active, amazing, and production-ready Telegram Bot.

## Phase 1: Real Data Acquisition (Scrapers)

- [ ] **Identify Target Websites**: Select 2-3 reliable scholarship portals (e.g., Scholaro, ScholarshipPortal, or regional government sites).
- [ ] **Implement Real Scrapers**:
  - [ ] Create `app/scrapers/sources/site_one_scraper.py` using `BeautifulSoup` or `httpx` (or `Playwright` for JS-heavy sites).
  - [ ] Create `app/scrapers/sources/site_two_scraper.py`.
  - [ ] Map the scraped HTML data to the `ScrapedScholarship` dataclass accurately.
- [ ] **Update Scraper Runner**: Modify `app/scrapers/runner.py` to iterate through and execute all implemented scrapers instead of just `SampleSourceScraper`.
- [ ] **Data Cleaning & Normalization**: Add utility functions to standardize country names, study levels (e.g., mapping "MSc" to "Master"), and funding types before inserting them into the DB.

## Phase 2: Telegram Bot UX/UI Excellence

- [ ] **Onboarding Wizard**: Create a step-by-step onboarding flow for new users `/start` to set their preferences (Country, Level, Field of Study).
- [ ] **Interactive Menus (Inline Keyboards)**:
  - [ ] Add a "🔍 Search Now" button to find scholarships immediately.
  - [ ] Add a "⚙️ Settings/Filters" button to update notification preferences.
  - [ ] Add pagination for search results (e.g., "Page 1 of 5 ➡️").
- [ ] **Rich Formatting**: Format the scholarship output messages beautifully using Telegram's HTML or MarkdownV2 parse mode (bold titles, clear links, emojis for deadlines/amounts).
- [ ] **Help & Support Commands**: Implement user-friendly `/help` and `/about` commands.

## Phase 3: Notifications & Scheduling

- [ ] **Configure the Scheduler**: Wrap `app/jobs/notification_job.py` and `app/scrapers/runner.py` in a robust scheduler like `APScheduler` or `Celery` to run automatically (e.g., scrape daily at 2 AM, notify users at 9 AM).
- [ ] **Smart Notifications**: Ensure `notification_job.py` only sends _new_ scholarships to users matching their specific filters, preventing spam.
- [ ] **Cleanup Job Activation**: Automate `cleanup_job.py` to remove expired scholarships from the database so users don't see dead links.

## Phase 4: Production Deployment

- [ ] **Environment Hardening**: Ensure all sensitive variables (Telegram Token, DB credentials) are securely managed via `.env` or secrets managers.
- [ ] **Database Migration**: Set up a managed PostgreSQL database (e.g., AWS RDS, Supabase, or DigitalOcean) and run Alembic migrations against it.
- [ ] **Logging and Monitoring**:
  - [ ] Integrate a logging tool (e.g., Sentry or standard python logging to files) to catch scraper failures or API errors.
  - [ ] Add basic analytics (e.g., track how many users are active, how many notifications are sent).
- [ ] **Dockerization Pipeline**:
  - [ ] Verify `docker-compose.yml` for production use.
  - [ ] Deploy to a VPS or cloud provider (e.g., Render, Railway, DigitalOcean Droplet).
- [ ] **Webhook vs Polling**: Transition the Telegram bot from long-polling to Webhooks for better performance and scalability in production.
