from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from sqlalchemy import select
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from app.db.models import StudyLevel, UserProfile
from app.db.session import SessionLocal


class OnboardingState(IntEnum):
    COUNTRY = 1
    FIELD = 2
    LEVEL = 3
    MIN_BUDGET = 4
    MAX_BUDGET = 5


@dataclass(frozen=True)
class BudgetParseResult:
    value: int | None
    ok: bool


def _get_or_create_profile(telegram_id: int, full_name: str | None) -> UserProfile:
    with SessionLocal() as session:
        profile = session.scalar(select(UserProfile).where(UserProfile.telegram_id == telegram_id))
        if profile is None:
            profile = UserProfile(telegram_id=telegram_id, full_name=full_name)
            session.add(profile)
            session.commit()
            session.refresh(profile)
            return profile

        if full_name and not profile.full_name:
            profile.full_name = full_name
            session.commit()
            session.refresh(profile)

        return profile


def _update_profile(telegram_id: int, **fields: object) -> None:
    with SessionLocal() as session:
        profile = session.scalar(select(UserProfile).where(UserProfile.telegram_id == telegram_id))
        if profile is None:
            return

        for key, value in fields.items():
            setattr(profile, key, value)

        session.commit()


def _parse_budget(text: str) -> BudgetParseResult:
    text = text.strip().lower()
    if text == "skip":
        return BudgetParseResult(value=None, ok=True)

    if not text.isdigit():
        return BudgetParseResult(value=None, ok=False)

    return BudgetParseResult(value=int(text), ok=True)


def _profile_summary(telegram_id: int) -> str:
    with SessionLocal() as session:
        profile = session.scalar(select(UserProfile).where(UserProfile.telegram_id == telegram_id))
        if profile is None:
            return "No profile found yet. Use /start to begin onboarding."

        return (
            "Your profile:\n"
            f"- Name: {profile.full_name or 'N/A'}\n"
            f"- Country: {profile.country or 'N/A'}\n"
            f"- Field: {profile.field_of_study or 'N/A'}\n"
            f"- Level: {profile.study_level.value if profile.study_level else 'N/A'}\n"
            f"- Min budget (USD): {profile.min_budget_usd if profile.min_budget_usd is not None else 'N/A'}\n"
            f"- Max budget (USD): {profile.max_budget_usd if profile.max_budget_usd is not None else 'N/A'}\n"
            f"- Onboarding complete: {'yes' if profile.onboarding_complete else 'no'}"
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    if user is None or update.message is None:
        return OnboardingState.COUNTRY

    _get_or_create_profile(telegram_id=user.id, full_name=user.full_name)

    await update.message.reply_text(
        "Welcome to Scholar Scout V2! Let's set up your profile.\n"
        "Step 1/5: Which country are you applying from?"
    )
    return OnboardingState.COUNTRY


async def onboarding_set_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or update.effective_user is None:
        return OnboardingState.COUNTRY

    country = update.message.text.strip()
    if not country:
        await update.message.reply_text("Country cannot be empty. Please enter your country.")
        return OnboardingState.COUNTRY

    _update_profile(update.effective_user.id, country=country)
    await update.message.reply_text("Step 2/5: What is your field of study?")
    return OnboardingState.FIELD


async def onboarding_set_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or update.effective_user is None:
        return OnboardingState.FIELD

    field = update.message.text.strip()
    if not field:
        await update.message.reply_text("Field of study cannot be empty. Please enter it.")
        return OnboardingState.FIELD

    _update_profile(update.effective_user.id, field_of_study=field)
    keyboard = [["bachelors", "masters"], ["phd", "other"]]
    await update.message.reply_text(
        "Step 3/5: Choose your study level:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return OnboardingState.LEVEL


async def onboarding_set_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or update.effective_user is None:
        return OnboardingState.LEVEL

    level_text = update.message.text.strip().lower()
    if level_text not in {level.value for level in StudyLevel}:
        await update.message.reply_text(
            "Invalid level. Choose one of: bachelors, masters, phd, other.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[["bachelors", "masters"], ["phd", "other"]],
                one_time_keyboard=True,
                resize_keyboard=True,
            ),
        )
        return OnboardingState.LEVEL

    _update_profile(update.effective_user.id, study_level=StudyLevel(level_text))
    await update.message.reply_text(
        "Step 4/5: Enter your minimum budget in USD (numbers only), or type 'skip'.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return OnboardingState.MIN_BUDGET


async def onboarding_set_min_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or update.effective_user is None:
        return OnboardingState.MIN_BUDGET

    parsed = _parse_budget(update.message.text)
    if not parsed.ok:
        await update.message.reply_text("Please enter a valid number or 'skip'.")
        return OnboardingState.MIN_BUDGET

    _update_profile(update.effective_user.id, min_budget_usd=parsed.value)
    await update.message.reply_text("Step 5/5: Enter your maximum budget in USD, or type 'skip'.")
    return OnboardingState.MAX_BUDGET


async def onboarding_set_max_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or update.effective_user is None:
        return OnboardingState.MAX_BUDGET

    parsed = _parse_budget(update.message.text)
    if not parsed.ok:
        await update.message.reply_text("Please enter a valid number or 'skip'.")
        return OnboardingState.MAX_BUDGET

    with SessionLocal() as session:
        profile = session.scalar(select(UserProfile).where(UserProfile.telegram_id == update.effective_user.id))
        if profile is None:
            await update.message.reply_text("Profile not found. Please run /start again.")
            return OnboardingState.COUNTRY

        min_budget = profile.min_budget_usd
        max_budget = parsed.value
        if min_budget is not None and max_budget is not None and max_budget < min_budget:
            await update.message.reply_text("Max budget cannot be less than min budget. Please enter max again.")
            return OnboardingState.MAX_BUDGET

        profile.max_budget_usd = max_budget
        profile.onboarding_complete = True
        session.commit()

    await update.message.reply_text(
        "Onboarding complete. Use /profile to review your settings.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def _get_command_value(context: ContextTypes.DEFAULT_TYPE) -> str | None:
    if not context.args:
        return None
    value = " ".join(context.args).strip()
    return value or None


async def set_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_user is None:
        return

    country = _get_command_value(context)
    if not country:
        await update.message.reply_text("Usage: /set_country <country>")
        return

    _get_or_create_profile(update.effective_user.id, update.effective_user.full_name)
    _update_profile(update.effective_user.id, country=country)
    await update.message.reply_text(f"Country updated to: {country}")


async def set_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_user is None:
        return

    field = _get_command_value(context)
    if not field:
        await update.message.reply_text("Usage: /set_field <field of study>")
        return

    _get_or_create_profile(update.effective_user.id, update.effective_user.full_name)
    _update_profile(update.effective_user.id, field_of_study=field)
    await update.message.reply_text(f"Field of study updated to: {field}")


async def set_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_user is None:
        return

    level_text = _get_command_value(context)
    if not level_text:
        await update.message.reply_text("Usage: /set_level <bachelors|masters|phd|other>")
        return

    level_text = level_text.lower()
    if level_text not in {level.value for level in StudyLevel}:
        await update.message.reply_text("Invalid level. Use one of: bachelors, masters, phd, other.")
        return

    _get_or_create_profile(update.effective_user.id, update.effective_user.full_name)
    _update_profile(update.effective_user.id, study_level=StudyLevel(level_text))
    await update.message.reply_text(f"Study level updated to: {level_text}")


async def set_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_user is None:
        return

    if len(context.args) != 2:
        await update.message.reply_text("Usage: /set_budget <min|skip> <max|skip>")
        return

    min_parsed = _parse_budget(context.args[0])
    max_parsed = _parse_budget(context.args[1])
    if not min_parsed.ok or not max_parsed.ok:
        await update.message.reply_text("Both values must be numbers or 'skip'.")
        return

    min_budget = min_parsed.value
    max_budget = max_parsed.value
    if min_budget is not None and max_budget is not None and max_budget < min_budget:
        await update.message.reply_text("Max budget cannot be less than min budget.")
        return

    _get_or_create_profile(update.effective_user.id, update.effective_user.full_name)
    _update_profile(
        update.effective_user.id,
        min_budget_usd=min_budget,
        max_budget_usd=max_budget,
    )
    await update.message.reply_text(
        "Budget updated: "
        f"min={min_budget if min_budget is not None else 'skip'}, "
        f"max={max_budget if max_budget is not None else 'skip'}"
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_user is None:
        return

    summary = _profile_summary(update.effective_user.id)
    await update.message.reply_text(summary)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is not None:
        await update.message.reply_text("Onboarding canceled. Use /start anytime to restart.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END