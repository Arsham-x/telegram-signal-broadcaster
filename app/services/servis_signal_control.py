# -*- coding: utf-8 -*-
import json
import os
from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from app.settings.config import (
    SIGNAL_LOG_FILE,
    SIGNAL_TEXTS_FILE,
)


# ---------- load ----------
def load_signal_logs():
    if os.path.exists(SIGNAL_LOG_FILE):
        try:
            with open(SIGNAL_LOG_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return json.loads(content) if content else []
        except (json.JSONDecodeError, OSError):
            return []
    return []

def load_signal_texts():
    if os.path.exists(SIGNAL_TEXTS_FILE):
        try:
            with open(SIGNAL_TEXTS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return json.loads(content) if content else {}
        except (json.JSONDecodeError, OSError):
            return {}
    return {}

# ---------- keyboards ----------
def signal_list_keyboard(logs):
    buttons = []

    for s in logs:

        real_index = s["_real_index"]

        signal_id = s.get(
            "signal_id",
            real_index + 1
        )

        entries = s.get("entries", [])

        if entries:
            entry_price = entries[0]
        else:
            entry_price = "-"

        label = (
            f"{signal_id} | "
            f"{s.get('symbol', '-')} | "
            f"{s.get('position', '-')} | "
            f"{entry_price}"
        )

        # =============== CLOR PRIC SIGNAL  ===========================

        position = str(
            s.get("position", "")
        ).strip().lower()

        if position in ("buy", "long"):
            button_style = "success"

        elif position in ("sell", "short"):
            button_style = "danger"

        else:
            button_style = "primary"

        # =====================================================
        # ساخت دکمه
        # =====================================================

        button_kwargs = {
            "text": label,
            "callback_data": f"manage_signal:{real_index}"
        }

        if button_style:
            button_kwargs["style"] = button_style

        buttons.append([
            InlineKeyboardButton(
                **button_kwargs
            )
        ])

    # =========================================================
    # دکمه حذف فقط برای لیست مدیریت
    # =========================================================

    buttons.append([
        InlineKeyboardButton(
            "🗑 حذف سیگنال از لیست",
            callback_data="signal_hide_mode"
        )
    ])

    return InlineKeyboardMarkup(buttons)

def signal_manage_keyboard(index: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ فعال", callback_data=f"signal_active:{index}"),
            InlineKeyboardButton("⛔ غیرفعال", callback_data=f"signal_deactive:{index}")
        ]
    ])

def signal_deactive_reasons_keyboard(index: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ کنسل شد", callback_data=f"signal_reason:cancel:{index}")],
        [InlineKeyboardButton("🛑 حد ضرر", callback_data=f"signal_reason:sl:{index}")],
        [InlineKeyboardButton("🎯 حد سود", callback_data=f"signal_reason:tp:{index}")],
        [InlineKeyboardButton("🚪 خروج فوری", callback_data=f"signal_reason:exit:{index}")],
        [InlineKeyboardButton("🟡 بریک ایون", callback_data=f"signal_reason:be:{index}")]
    ])
    
    
def signal_tp_keyboard(index: int, tp_count: int):
    buttons = []

    for i in range(tp_count):
        buttons.append([
            InlineKeyboardButton(
                f"🎯 TP{i+1}",
                callback_data=f"signal_tp:{index}:{i+1}"
            )
        ])

    return InlineKeyboardMarkup(buttons)
    
    
def signal_market_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📈 فارکس", "🪙 کریپتو"],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )    
    