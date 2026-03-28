from __future__ import annotations

import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.bot.client.api_client import BackendApiClient

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to Scholarship Scout Bot. Use /help to see commands.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Commands: /start, /help, /filters, /latest")


async def filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Filter management is available via backend endpoints.")


async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    api_client = BackendApiClient(API_BASE_URL)
    try:
        rows = await api_client.latest_scholarships(limit=5)
    except Exception:
        await update.message.reply_text("Backend is currently unavailable. Please try again later.")
        return

    if not rows:
        await update.message.reply_text("No scholarships found yet.")
        return

    lines = [f"- {row['title']}" for row in rows]
    await update.message.reply_text("Latest scholarships:\n" + "\n".join(lines))


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("filters", filters))
    app.add_handler(CommandHandler("latest", latest))
    app.run_polling()


if __name__ == "__main__":
    main()
