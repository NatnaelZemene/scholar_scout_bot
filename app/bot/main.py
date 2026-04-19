from __future__ import annotations

import os

from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.bot.onboarding import (
    OnboardingState,
    cancel,
    profile,
    onboarding_set_country,
    onboarding_set_field,
    onboarding_set_level,
    onboarding_set_max_budget,
    onboarding_set_min_budget,
    set_budget,
    set_country,
    set_field,
    set_level,
    start,
)


def build_application(bot_token: str) -> Application:
    app = Application.builder().token(bot_token).build()

    onboarding_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            OnboardingState.COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_set_country)],
            OnboardingState.FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_set_field)],
            OnboardingState.LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_set_level)],
            OnboardingState.MIN_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_set_min_budget)],
            OnboardingState.MAX_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_set_max_budget)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(onboarding_handler)
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("set_country", set_country))
    app.add_handler(CommandHandler("set_field", set_field))
    app.add_handler(CommandHandler("set_level", set_level))
    app.add_handler(CommandHandler("set_budget", set_budget))
    app.add_handler(CommandHandler("cancel", cancel))
    return app


def main() -> None:
    load_dotenv()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required in environment variables.")

    app = build_application(bot_token)
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()