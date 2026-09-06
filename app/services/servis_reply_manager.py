# -*- coding: utf-8 -*-
import json
import os
from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from app.settings.config import REPLY_TEXTS_FILE, atomic_json_write
def load_reply_texts():
    if os.path.exists(REPLY_TEXTS_FILE):
        try:
            with open(REPLY_TEXTS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return json.loads(content) if content else []
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_reply_texts(texts):
    atomic_json_write(REPLY_TEXTS_FILE, texts)


def reply_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["➕ جمله آماده"],
            ["📋 پیام آماده"],
            ["⌨️ پیام دستی"],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )

def reply_market_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📈 فارکس", "🪙 کریپتو"],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )
# ---------- Saved Texts ----------
def reply_text_manage_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["➕ افزودن جمله"],
            ["🗂 مدیریت جملات"],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )

def reply_signal_keyboard(logs, prefix="reply_signal"):
    buttons = []

    for s in logs:

        real_index = s["_real_index"]

        label = f"{real_index + 1} | {s.get('symbol','-')}"

        buttons.append([
            InlineKeyboardButton(
                label,
                callback_data=f"{prefix}:{real_index}"
            )
        ])

    return InlineKeyboardMarkup(buttons)
def reply_saved_texts_keyboard(texts):
    buttons = []

    for i, txt in enumerate(texts):
        short = txt if len(txt) <= 35 else txt[:35] + "..."

        buttons.append([
            InlineKeyboardButton(
                short,
                callback_data=f"reply_send:{i}"
            )
        ])

    return InlineKeyboardMarkup(buttons)
def reply_texts_inline_keyboard(texts):
    buttons = []

    for i, txt in enumerate(texts):
        short = txt if len(txt) <= 35 else txt[:35] + "..."

        buttons.append([
            InlineKeyboardButton(
                f"🗑 {short}",
                callback_data=f"reply_delete:{i}"
            )
        ])

    return InlineKeyboardMarkup(buttons)