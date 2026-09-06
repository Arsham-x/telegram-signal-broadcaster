# -*- coding: utf-8 -*-
import json
import os
from telegram import ReplyKeyboardMarkup

from app.settings.config import SYMBOLS_FILE, atomic_json_write


def load_symbols():
    if not os.path.exists(SYMBOLS_FILE):
        return {
            "crypto": [],
            "forex": []
        }

    try:
        with open(SYMBOLS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # اگر فایل قدیمی بود
        if isinstance(data, list):
            return {
                "crypto": data,
                "forex": []
            }

        return data

    except Exception:
        return {
            "crypto": [],
            "forex": []
        }


def save_symbols(data):
    atomic_json_write(SYMBOLS_FILE, data)


def get_symbols(category):
    data = load_symbols()
    return data.get(category, [])


def add_symbol(category, symbol):
    data = load_symbols()

    if symbol not in data[category]:
        data[category].append(symbol)

    save_symbols(data)


def remove_symbol(category, symbol):
    data = load_symbols()

    if symbol in data[category]:
        data[category].remove(symbol)

    save_symbols(data)


def category_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["🪙 کریپتو", "📈 فارکس"],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )


def symbol_action_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["➕ افزودن نماد", "🗑 حذف نماد"],
            ["📋 لیست نمادها"],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )


def symbols_keyboard(symbols):
    keyboard = []

    for s in symbols:
        keyboard.append([s])

    keyboard.append(["🔙 بازگشت"])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )