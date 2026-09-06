# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import json
import os

from app.settings.config import (
    CHANNELS_FILE,
)
def load_channels():
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_channels(channels):
    with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

def channel_manage_keyboard():
    keyboard = [
        ["➕ افزودن کانال یا گروه"],
        ["📃 لیست کانال یا گروه"],
        ["👥 مدیریت کامیونیتی"],
        ["🔙 بازگشت"]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

def channels_list_inline_keyboard(channels):
    buttons = []
    for ch in channels:
        label = ch.get("title") or str(ch["chat_id"])
        buttons.append([
            InlineKeyboardButton(
                f"🗑 حذف {label}",
                callback_data=f"del_channel:{ch['chat_id']}"
            )
        ])
    return InlineKeyboardMarkup(buttons)
def channel_category_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["🪙 کریپتو", "📈 فارکس"],
            ["🔀 هر دو"],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )
async def validate_chat(bot, chat_id_or_username: str):
    try:
        chat = await bot.get_chat(chat_id_or_username)

        if chat.type not in ["group", "supergroup", "channel"]:
            return False, "این آیدی مربوط به گروه یا کانال نیست."

        me = await bot.get_me()
        member = await bot.get_chat_member(chat.id, me.id)

        if member.status not in ["administrator", "creator"]:
            return False, "ربات داخل این گروه/کانال ادمین نیست."

        return True, {
            "chat_id": chat.id,
            "title": chat.title or chat.username or str(chat.id),
            "type": chat.type,
            "category": None
        }

    except Exception as e:
        print("validate_chat error:", e) 
        return False, "این آیدی یا یوزرنیم معتبر نیست."