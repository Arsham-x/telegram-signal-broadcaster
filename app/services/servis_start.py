# -*- coding: utf-8 -*-
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from app.settings.config import ADMIN_ID

from app.services.servis_user_manager import (
    get_user_by_id,
    is_owner,
    is_admin,
    register_user,
)
from app.services import servis_keyboard as keyboard_service
from app.services.servis_signal_control import load_signal_logs


# =========================================================
# آمار خلاصه سیگنال‌ها
# =========================================================

_CLOSED_STATUSES = {"cancel", "sl", "exit", "full_tp"}


def _quick_stats() -> str:
    """یک خط آمار برای پیام خوش‌آمدگویی."""
    try:
        logs = load_signal_logs()
    except Exception:
        return ""

    if not logs:
        return ""

    active = 0
    today_count = 0
    today_str = datetime.now().strftime("%Y-%m-%d")

    for sig in logs:
        status = sig.get("status", "active")
        if status not in _CLOSED_STATUSES:
            active += 1
        if sig.get("date", "").startswith(today_str):
            today_count += 1

    return (
        f"\n\n📈 سیگنال‌های فعال: {active}"
        f" | امروز: {today_count}"
    )
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    users = context.application.bot_data.get("users", [])

    users = register_user(
        users,
        update
    )

    context.application.bot_data["users"] = users

    if update.effective_chat.type != "private":
        return

    user_id = update.effective_user.id

    user = get_user_by_id(
        users,
        user_id
    )

    # =====================================================
    # BANNED
    # =====================================================

    if user and user.get("is_banned"):

        await update.message.reply_text(
            "⛔ شما بن شده‌اید."
        )

        return

    # =====================================================
    # OWNER
    # =====================================================

    owner = is_owner(
        user_id,
        ADMIN_ID
    )

    # =====================================================
    # ADMIN
    # =====================================================

    admin = is_admin(
        users,
        user_id,
        ADMIN_ID
    )

    # =====================================================
    # NORMAL USER
    # =====================================================

    if not owner and not admin:

        # هیچ کیبوردی برای کاربر عادی نمایش داده نمی‌شود
        await update.message.reply_text(
            "شما دسترسی ندارید."
        )

        return

    # =====================================================
    # OWNER / ADMIN KEYBOARD
    # =====================================================

    stats = _quick_stats()

    await update.message.reply_text(
        f"سلام 👋{stats}",
        reply_markup=keyboard_service.main_keyboard(
            is_owner=owner,
            is_admin=admin
        )
    )


