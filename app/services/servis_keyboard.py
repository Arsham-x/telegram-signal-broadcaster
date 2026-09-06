# -*- coding: utf-8 -*-
from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

SYMBOLS_PER_PAGE = 10
# ================== KEYBOARDS ==================
def main_keyboard(is_owner: bool = False, is_admin: bool = False):

    # =====================================================
    # OWNER
    # =====================================================

    if is_owner:

        keyboard = [
            ["👥 مدیریت کاربران", "🪙 اد نماد"],
            ["📊 گزارش گیری", "🚀 سیگنال جدید"],
            ["⚙️ مدیریت سیگنال"],
            ["📢 مدیریت چنل"],
            ["💬 ریپلای به سیگنال"],
            ["📣 ارسال پیام همگانی"],
        ]

    # =====================================================
    # ADMIN
    # =====================================================

    elif is_admin:

        keyboard = [
            ["🪙 اد نماد"],
            ["📊 گزارش گیری", "🚀 سیگنال جدید"],
            ["⚙️ مدیریت سیگنال"],
            ["📢 مدیریت چنل"],
            ["💬 ریپلای به سیگنال"],
            ["📣 ارسال پیام همگانی"],
        ]

    # =====================================================
    # NORMAL USER
    # =====================================================

    else:

        return None

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def paginated_symbols_keyboard(page: int, symbols: list[str]):
    start = page * SYMBOLS_PER_PAGE
    end = start + SYMBOLS_PER_PAGE

    keyboard = []

    for s in symbols[start:end]:
        keyboard.append([s])

    nav = []

    if page > 0:
        nav.append("⬅️ قبلی")

    if end < len(symbols):
        nav.append("➡️ بعدی")

    if nav:
        keyboard.append(nav)

    keyboard.append(["🔙 بازگشت"])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )    
    


def report_time_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1 ماه گذشته", callback_data="report_time_1m")],
        [InlineKeyboardButton("3 ماه گذشته", callback_data="report_time_3m")],
        [InlineKeyboardButton("6 ماه گذشته", callback_data="report_time_6m")],
        [InlineKeyboardButton("1 سال گذشته", callback_data="report_time_1y")],
        [InlineKeyboardButton("🗑 پاک کردن گزارش‌ها", callback_data="report_delete")]
    ])
