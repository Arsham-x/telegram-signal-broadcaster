# ================== PYTHON ==================

import asyncio

from datetime import time
from zoneinfo import ZoneInfo


# ================== TELEGRAM ==================

from telegram import Update

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)


# ================== CONFIG ==================

from app.settings.config import (
    TOKEN,
    ADMIN_ID,
    SYMBOLS_FILE,
    SYMBOLS_PER_PAGE,
    DAILY_REPORT_HOUR,
    DAILY_REPORT_MINUTE,
    DAILY_REPORT_TIMEZONE,
)


# ================== SERVICES ==================

from app.services.servis_user_manager import (
    get_user_by_id,
    is_owner,
    is_admin,
)


from app.services import servis_keyboard as keyboard_service


# ================== HANDLERS ==================

from app.handlers.reset_user_flow_handler import (
    reset_user_flow,
)

from app.handlers.report_handler import (
    handle_report,
)

from app.handlers.channel_manage_handler import (
    handle_channel_manage,
)

from app.handlers.community_manage_handler import (
    handle_community_manage,
)

from app.handlers.user_manage_handler import (
    handle_user_manage,
)

from app.handlers.signal_manage_handler import (
    handle_signal_manage,
)

from app.handlers.signal_management_handler import (
    handle_signal_management,
)

from app.handlers.reply_signal_handler import (
    handle_reply_signal,
)

from app.handlers.broadcast_handler import (
    handle_broadcast,
)

from app.handlers.symbol_manage_handler import (
    handle_symbol_manage,
)


# دکمه‌های منوی اصلی؛ ورود تازه به یک فلو.
MAIN_MENU_BUTTONS = frozenset({
    "👥 مدیریت کاربران",
    "🪙 اد نماد",
    "📊 گزارش گیری",
    "🚀 سیگنال جدید",
    "⚙️ مدیریت سیگنال",
    "📢 مدیریت چنل",
    "👥 مدیریت کامیونیتی",
    "💬 ریپلای به سیگنال",
    "📣 ارسال پیام همگانی",
})



async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()


    users = context.application.bot_data.get("users", [])
    user = get_user_by_id(users, user_id)
    if user and user.get("is_banned"):
        await update.message.reply_text("⛔ شما بن شده‌اید.")
        return

    if not is_admin(users, user_id, ADMIN_ID):
        await update.message.reply_text("شما دسترسی ندارید.")
        return
    context.user_data.setdefault("waiting_for_symbol", False)
    context.user_data.setdefault("waiting_for_signal_symbol", False)
    context.user_data.setdefault("waiting_for_signal_flow", False)
    context.user_data.setdefault("symbol_page", 0)
    context.user_data.setdefault("symbol_flow", False)
    context.user_data.setdefault("waiting_for_symbol", False)
    context.user_data.setdefault("waiting_for_signal_symbol", False)
    context.user_data.setdefault("symbol_category", None)
    context.user_data.setdefault("symbol_action", None)
    # ================== بازگشت ==================
    if text == "🔙 بازگشت":
    
        reset_user_flow(context)
    
        owner = is_owner(
            user_id,
            ADMIN_ID
        )
    
        admin = is_admin(
            users,
            user_id,
            ADMIN_ID
        )
    
        await update.message.reply_text(
            "برگشتیم.",
            reply_markup=keyboard_service.main_keyboard(
                is_owner=owner,
                is_admin=admin
            )
        )
    
        return
    # ================== دکمه‌های منوی اصلی ==================
    # همیشه از فلو نیمه‌کاره قبلی خارج می‌شوند؛
    # state مانده نباید بتواند این دکمه‌ها را ببلعد.
    if text in MAIN_MENU_BUTTONS:
        reset_user_flow(context)

    context.user_data.setdefault("waiting_for_report_channel", False)
    context.user_data.setdefault("waiting_for_user_action", False)
    context.user_data.setdefault("selected_user_id", None)
    context.user_data.setdefault("waiting_for_channel_add", False)
    context.user_data.setdefault("community_mode", None)
    context.user_data.setdefault("community_category", None)
    context.user_data.setdefault("community_name", None)
    context.user_data.setdefault("community_delete_category", None)
    context.user_data.setdefault("community_delete_index", None)
    context.user_data.setdefault("community_delete_channels", [])
    context.user_data.setdefault("community_delete_selected", [])
    
    # ================== گزارش گیری ==================
    
    handled = await handle_report(
        update,
        context
    )
    
    if handled:
        return


    # ================== مدیریت کانال و گروه ==================

    handled = await handle_channel_manage(
        update,
        context
    )
    
    if handled:
        return
    
    
    # ================== مدیریت کامیونیتی ==================
    
    handled = await handle_community_manage(
        update,
        context
    )
    
    if handled:
        return
    # ================== مدیریت کاربران (فقط OWNER) ==================
    handled = await handle_user_manage(
        update,
        context
    )
    
    if handled:
        return
    
    # ================== SIGNAL NEW ==================
    
    if (
        text == "🚀 سیگنال جدید"
        or context.user_data.get("waiting_for_signal_market")
        or context.user_data.get("waiting_for_signal_symbol")
        or context.user_data.get("waiting_for_signal_flow")
    ):
        return await handle_signal_manage(
            update,
            context
        )
    
    
    # ================== SIGNAL MANAGEMENT ==================
    
    handled = await handle_signal_management(
        update,
        context
    )
    
    if handled:
        return

    
    # ================== REPLY TO SIGNAL ==================
    
    handled = await handle_reply_signal(
        update,
        context
    )
    
    if handled:
        return


    # ================== BROADCAST ==================
    
    handled = await handle_broadcast(
        update,
        context
    )
    
    if handled:
        return
    
    # ================== مدیریت نمادها =================

    handled = await handle_symbol_manage(
        update,
        context
    )
    
    if handled:
        return
