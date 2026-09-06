# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ContextTypes

from app.services.servis_channel_manager import (
    load_channels,
    save_channels,
    channels_list_inline_keyboard
)

from app.services.servis_user_manager import get_user_by_id
async def channel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    users = context.application.bot_data.get("users", [])
    user = get_user_by_id(users, user_id)
    if user and user.get("is_banned"):
        await query.answer("⛔ شما بن شده‌اید.", show_alert=True)
        return

    data = query.data

    if data.startswith("del_channel:"):
        chat_id = int(data.split(":")[1])

        channels = load_channels()
        channels = [c for c in channels if c["chat_id"] != chat_id]
        save_channels(channels)

        await query.answer("حذف شد ✅", show_alert=False)

        if channels:
            await query.edit_message_reply_markup(
                reply_markup=channels_list_inline_keyboard(channels)
            )
        else:
            await query.edit_message_text("لیست خالی شد.")

