# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ContextTypes

from app.services import servis_channel_manager as channel_manager

from app.services.servis_channel_manager import (
    channel_manage_keyboard,
    load_channels,
    save_channels,
    channels_list_inline_keyboard,
    validate_chat,
    channel_category_keyboard,
)


async def handle_channel_manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = (update.message.text or "").strip()

    # =====================================================
    # مدیریت کانال و گروه
    # =====================================================

    if text == "📢 مدیریت چنل":

        await update.message.reply_text(
            "مدیریت کانال و گروه:",
            reply_markup=channel_manage_keyboard()
        )

        return True

    # =====================================================
    # افزودن کانال یا گروه
    # =====================================================

    if text == "➕ افزودن کانال یا گروه":
        context.user_data["community_mode"] = None
        context.user_data["community_category"] = None
        context.user_data["community_name"] = None
        context.user_data["waiting_community_name"] = False
        context.user_data["community_channels"] = None
        context.user_data["community_selected"] = []
        context.user_data["community_page"] = 0
        context.user_data["waiting_delete_community"] = False
        context.user_data["community_delete_category"] = None
        context.user_data["delete_community_index"] = None
        context.user_data["delete_inside_mode"] = False
        context.user_data["delete_inside_selected"] = []
        context.user_data["waiting_for_channel_add"] = True
        context.user_data["waiting_for_channel_category"] = False
        context.user_data["new_channel"] = None

        await update.message.reply_text(
            "آیدی عددی یا یوزرنیم کانال/گروه را بفرست:"
        )

        return True

    # =====================================================
    # دریافت آیدی کانال / گروه
    # =====================================================

    if context.user_data.get("waiting_for_channel_add"):

        ok, result = await validate_chat(
            context.application.bot,
            text
        )

        if not ok:

            await update.message.reply_text(
                f"❌ {result}"
            )

            return True

        context.user_data["new_channel"] = result
        context.user_data["waiting_for_channel_add"] = False
        context.user_data["waiting_for_channel_category"] = True

        await update.message.reply_text(
            "این کانال/گروه برای کدام بازار است؟",
            reply_markup=channel_category_keyboard()
        )

        return True

    # =====================================================
    # انتخاب دسته کانال
    # =====================================================

    if context.user_data.get("waiting_for_channel_category"):

        category_map = {
            "🪙 کریپتو": "crypto",
            "📈 فارکس": "forex",
            "🔀 هر دو": "both"
        }

        if text not in category_map:
            await update.message.reply_text(
                "این کانال/گروه برای کدام بازار است؟",
                reply_markup=channel_category_keyboard()
            )
            return True

        channel = context.user_data.get("new_channel")

        if not channel:

            await update.message.reply_text(
                "خطا. دوباره تلاش کن."
            )

            return True

        channel["category"] = category_map[text]

        channels = channel_manager.load_channels()

        if any(
            ch["chat_id"] == channel["chat_id"]
            for ch in channels
        ):

            await update.message.reply_text(
                "این کانال/گروه قبلاً ثبت شده."
            )

            context.user_data["waiting_for_channel_category"] = False
            context.user_data["new_channel"] = None

            return True

        channels.append(channel)

        save_channels(channels)

        context.user_data["waiting_for_channel_category"] = False
        context.user_data["new_channel"] = None

        await update.message.reply_text(
            "✅ کانال/گروه با دسته‌بندی ذخیره شد."
        )

        return True

    # =====================================================
    # لیست کانال‌ها و گروه‌ها
    # =====================================================

    if text == "📃 لیست کانال یا گروه":

        channels = channel_manager.load_channels()

        if not channels:

            await update.message.reply_text(
                "لیست خالی است."
            )

            return True

        await update.message.reply_text(
            "لیست کانال‌ها و گروه‌ها:",
            reply_markup=channels_list_inline_keyboard(
                channels
            )
        )

        return True

    # =====================================================
    # چیزی مربوط به مدیریت کانال نبود
    # =====================================================

    return False
