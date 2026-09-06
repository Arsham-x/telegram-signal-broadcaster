# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import asyncio


def _get_token():
    env_token = os.environ.get("BOT_TOKEN", "").strip()
    if env_token:
        return env_token
    from app.settings.config import TOKEN as config_token
    return config_token


# =========== CHANEL ==========
from app.services import servis_channel_manager as channel_manager

from app.services.servis_channel_manager import (
    channel_manage_keyboard,
    load_channels,
    save_channels,
    channels_list_inline_keyboard,
    validate_chat,
    channel_category_keyboard, 
)
import app.services.servis_community_manager as community_manager
import app.services.servis_broadcast_manager as broadcast_manager

# =========== USER ============
from app.services.servis_user_manager import (
    load_users,
    save_users,
    get_user_by_id,
    is_owner,
    is_admin,
    register_user,
    user_list_keyboard,
    user_action_keyboard,
)
# =========== SIGNAL ============
from app.services import servis_signal_manager as signal_manager
from app.services import servis_signal_control as signal_control
from app.handlers.signal_manage_handler import handle_signal_manage
from app.services import servis_reply_manager as reply_manager
from app.services import servis_symbol_manager as symbol_manager
# ========== CONFIG ============
from app.settings.config import (
    TOKEN,
    ADMIN_ID,
    SYMBOLS_FILE,
    SYMBOLS_PER_PAGE,
    DAILY_REPORT_HOUR,
    DAILY_REPORT_MINUTE,
    DAILY_REPORT_TIMEZONE,
)
from datetime import time
from zoneinfo import ZoneInfo
# ================== LOAD ==================

from app.services.servis_load import load_data, save_symbols
# ================== REPORT =====================
from app.services.servis_daily_report import send_daily_reports
# ================== KEYBOARDS ==================
from app.services import servis_keyboard as keyboard_service
# ================== REPORTtMANAGER ==================
from app.services import servis_report_manager as report_manager
# ================== START ==================
from app.services.servis_start import start
# ==================  STAT  ==================
from app.handlers.reset_user_flow_handler import reset_user_flow
# ================== HANDLE ==================
from app.handlers.handler import handle
# ================== RUN ==================
async def post_init(application):

    await load_data(application)

    # =====================================================
    # DAILY REPORT SCHEDULER
    # =====================================================

    if application.job_queue is None:

        print(
            "ERROR: JobQueue is not available."
        )

        return

    application.job_queue.run_daily(
        send_daily_reports,

        time=time(
            hour=DAILY_REPORT_HOUR,
            minute=DAILY_REPORT_MINUTE,
            tzinfo=DAILY_REPORT_TIMEZONE
        ),

        name="daily_signal_reports"
    )

    print(
        "DAILY REPORT SCHEDULER REGISTERED | "
        f"{DAILY_REPORT_HOUR:02d}:"
        f"{DAILY_REPORT_MINUTE:02d} "
        f"{DAILY_REPORT_TIMEZONE}"
    )
def main():

    token = _get_token()

    builder = Application.builder().token(token).post_init(post_init)

    proxy_url = os.environ.get("BOT_PROXY", "").strip()
    if proxy_url:
        print(f"USING PROXY | {proxy_url.split('@')[-1]}")
        builder = (
            builder
            .proxy(proxy_url)
            .get_updates_proxy(proxy_url)
        )

    application = builder.build()


    # ================= COMMANDS =================

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    # ================= TEXT HANDLER =================

    application.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & ~filters.COMMAND,
            handle
        )
    )


    # ================= CALLBACKS =================

    from app.callbacks.callback import register_callbacks

    print("CALLBACKS REGISTERED")

    register_callbacks(application)


    print("Bot is running...")

    application.run_polling()

if __name__ == "__main__":
    main()