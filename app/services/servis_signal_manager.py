# -*- coding: utf-8 -*-
from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

import json
import os
import asyncio
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from app.settings.config import (
    SIGNAL_LOG_FILE,
    COMMUNITIES_FILE,
)

signal_state = {}


# =========================================================
# STATE
# =========================================================

def reset_signal(user_id: int):
    signal_state[user_id] = {
        "market": None,
        "symbol": None,
        "position": None,
        "leverage": None,
        "order_type": None,

        "waiting_for_tp": False,
        "entries": [],
        "entry_done": False,
        "waiting_for_entry": False,

        "sl": None,
        "tps": [],

        "step": "symbol",

        "selected_communities": [],
        "selected_channels": [],

        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def clear_signal_session(context, user_id):
    """
    پاک کردن کامل session ساخت سیگنال
    """

    context.user_data.pop("signal_market", None)
    context.user_data.pop("signal_symbols", None)
    context.user_data.pop("symbol_page", None)

    context.user_data.pop("waiting_for_signal_market", None)
    context.user_data.pop("waiting_for_signal_symbol", None)
    context.user_data.pop("waiting_for_signal_flow", None)

    context.user_data.pop("signal", None)

    signal_state.pop(user_id, None)


# =========================================================
# KEYBOARDS
# =========================================================

def position_keyboard(market):

    if market == "crypto":
        keyboard = [
            ["SHORT", "LONG"],
            ["🔙 بازگشت"]
        ]
    else:
        keyboard = [
            ["BUY", "SELL"],
            ["🔙 بازگشت"]
        ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def order_type_keyboard():

    return ReplyKeyboardMarkup(
        [
            ["مارکت", "تعیین حد"],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )


def tp_keyboard():

    return ReplyKeyboardMarkup(
        [
            ["➕ Tp اضافه", "✅ تمام"],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )


def entry_keyboard():

    return ReplyKeyboardMarkup(
        [
            ["➕ Entry اضافه", "✅ ادامه"],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )


def signal_preview_keyboard():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ ادامه",
                    callback_data="signal_preview_continue"
                ),
                InlineKeyboardButton(
                    "❌ لغو",
                    callback_data="signal_preview_cancel"
                )
            ]
        ]
    )


def back_keyboard():

    return ReplyKeyboardMarkup(
        [["🔙 بازگشت"]],
        resize_keyboard=True
    )


# =========================================================
# COMMUNITIES (with in-memory cache)
# =========================================================

_communities_cache = None
_communities_mtime = 0.0


def _invalidate_communities_cache():
    """بعد از هر تغییر در communities.json صدا بزن."""
    global _communities_cache, _communities_mtime
    _communities_cache = None
    _communities_mtime = 0.0


def load_communities():
    """
    خواندن communities.json — با cache.
    فقط وقتی فایل تغییر کرده دوباره میخونه.
    """
    global _communities_cache, _communities_mtime

    if not os.path.exists(COMMUNITIES_FILE):
        return []

    try:
        mtime = os.path.getmtime(COMMUNITIES_FILE)
    except OSError:
        return _communities_cache or []

    if _communities_cache is not None and mtime == _communities_mtime:
        return _communities_cache

    try:
        with open(
            COMMUNITIES_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read().strip()

            if not content:
                _communities_cache = []
                _communities_mtime = mtime
                return []

            data = json.loads(content)

            if not isinstance(data, list):
                _communities_cache = []
                _communities_mtime = mtime
                return []

            _communities_cache = data
            _communities_mtime = mtime
            return data

    except (json.JSONDecodeError, OSError):
        return _communities_cache or []


def get_market_communities(market):
    """
    فقط کامیونیتی‌های مربوط به market انتخاب‌شده را برمی‌گرداند.

    مثال:
    crypto -> فقط category == crypto
    forex  -> فقط category == forex
    """

    communities = load_communities()

    result = []

    for community in communities:

        if not isinstance(community, dict):
            continue

        category = str(
            community.get("category", "")
        ).strip().lower()

        if category != str(market).strip().lower():
            continue

        channels = community.get("channels", [])

        if not isinstance(channels, list):
            channels = []

        result.append(
            {
                "name": community.get(
                    "name",
                    "بدون نام"
                ),
                "category": category,
                "channels": channels
            }
        )

    return result


def get_community_by_name(market, name):
    """
    پیدا کردن یک کامیونیتی مشخص.
    """

    communities = get_market_communities(market)

    for community in communities:

        if community["name"] == name:
            return community

    return None


def get_channels_from_communities(
    market,
    selected_names=None,
    all_communities=False
):
    """
    کامیونیتی‌ها را به chat_idهای نهایی تبدیل می‌کند.

    channels می‌تواند شامل:
        - int
        - str
        - dict دارای chat_id

    خروجی:
        لیست chat_id بدون تکرار
    """

    communities = get_market_communities(market)

    if all_communities:

        selected = communities

    else:

        selected_names = selected_names or []

        selected = [
            community
            for community in communities
            if community["name"] in selected_names
        ]

    chat_ids = []

    for community in selected:

        channels = community.get(
            "channels",
            []
        )

        if not isinstance(channels, list):
            continue

        for channel in channels:

            # -----------------------------
            # channel به صورت dict
            # -----------------------------
            if isinstance(channel, dict):

                chat_id = channel.get(
                    "chat_id"
                )

            # -----------------------------
            # channel به صورت int / str
            # -----------------------------
            else:

                chat_id = channel

            if chat_id is None:
                continue

            if chat_id not in chat_ids:
                chat_ids.append(chat_id)

    print(
        "[SIGNAL CHAT IDS]",
        "market =", market,
        "all =", all_communities,
        "selected =", selected_names,
        "chat_ids =", chat_ids
    )

    return chat_ids
def communities_inline_keyboard(
    market,
    selected_names=None
):
    """
    کیبورد کامیونیتی‌های مربوط به market.

    اینجا دیگر channelها مستقیماً نمایش داده نمی‌شوند.
    فقط گروه‌های دسته‌بندی‌شده نمایش داده می‌شوند.
    """

    selected_names = selected_names or []

    communities = get_market_communities(market)

    buttons = []

    for community in communities:

        name = community["name"]

        checked = (
            "✅"
            if name in selected_names
            else "⬜️"
        )

        buttons.append(
            [
                InlineKeyboardButton(
                    f"{checked} {name}",
                    callback_data=f"toggle_community:{name}"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "📣 ارسال به همه کامیونیتی‌ها",
                callback_data="send_signal_all_communities"
            )
        ]
    )

    buttons.append(
        [
            InlineKeyboardButton(
                "🚀 ارسال به انتخاب‌شده‌ها",
                callback_data="send_signal_communities"
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


# =========================================================
# PERSISTENCE
# =========================================================

def _save_signal_log_sync(data: dict):
    """بخش sync ذخیره لاگ — در thread اجرا میشه."""

    logs = []

    if os.path.exists(SIGNAL_LOG_FILE):

        try:

            with open(
                SIGNAL_LOG_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                content = f.read().strip()

                logs = (
                    json.loads(content)
                    if content
                    else []
                )

        except (
            json.JSONDecodeError,
            OSError
        ):
            logs = []

    # =====================================================
    # SIGNAL ID
    # =====================================================
    max_signal_id = 0

    for signal in logs:

        if not isinstance(signal, dict):
            continue

        try:
            signal_id = int(
                signal.get("signal_id", 0)
            )
        except (TypeError, ValueError):
            signal_id = 0

        if signal_id > max_signal_id:
            max_signal_id = signal_id

    if not data.get("signal_id"):

        data["signal_id"] = max_signal_id + 1

    else:

        try:
            data["signal_id"] = int(
                data["signal_id"]
            )
        except (TypeError, ValueError):

            data["signal_id"] = max_signal_id + 1

    # =====================================================
    # MANAGEMENT VISIBILITY
    # =====================================================
    if "hidden_from_management" not in data:
        data["hidden_from_management"] = False

    # =====================================================
    # SAVE
    # =====================================================

    logs.append(data)

    os.makedirs(
        os.path.dirname(SIGNAL_LOG_FILE),
        exist_ok=True
    )

    with open(
        SIGNAL_LOG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            logs,
            f,
            ensure_ascii=False,
            indent=2
        )


async def save_signal_log(data: dict):
    """ذخیره لاگ سیگنال — بدون بلاک event loop."""
    await asyncio.to_thread(_save_signal_log_sync, data)


# =========================================================
# MESSAGE BUILDER
# =========================================================

def build_signal_message_premium(data: dict) -> str:

    emoji = {
        "green": '<tg-emoji emoji-id="5267231042934154418">🟢</tg-emoji>',
        "target": '<tg-emoji emoji-id="5310278924616356636">🎯</tg-emoji>',
        "sparkle": '<tg-emoji emoji-id="5325547803936572038">✨</tg-emoji>',
        "chart": '<tg-emoji emoji-id="5231200819986047254">📊</tg-emoji>',
        "hourglass": '<tg-emoji emoji-id="5325583469344989152">⏳</tg-emoji>',
        "top": '<tg-emoji emoji-id="5285364652555914660">🔝</tg-emoji>',
        "red": '<tg-emoji emoji-id="4990295687741572092">🔴</tg-emoji>',
    }

    lines = []

    lines.append(
        f"{emoji['top']} {data.get('symbol', '-')}"
    )

    lines.append(
        f"{emoji['target']}"
    )

    lines.append("")

    lines.append(
        f"{emoji['chart']} Signal position: "
        f"{data.get('position', '-')}"
    )

    lines.append(
        f"{emoji['hourglass']} "
        f"{data.get('order_type', '-')} Order"
    )

    leverage = str(
        data.get("leverage", "")
    ).strip()

    if leverage and leverage != "0":
        lines.append(
            f"{emoji['sparkle']} "
            f"Leverage: {leverage}"
        )

    lines.append("")

    for i, entry in enumerate(
        data.get("entries", []),
        1
    ):

        lines.append(
            f"{emoji['green']} "
            f"Entry {i}: {entry}"
        )

    lines.append("")

    lines.append(
        f"{emoji['red']} "
        f"SL: {data.get('sl', '-')}"
    )

    lines.append("")

    for i, tp in enumerate(
        data.get("tps", []),
        1
    ):

        lines.append(
            f"{emoji['target']} "
            f"TP{i}: {tp}"
        )

    lines.append("")

    lines.append("🎯 Free & Update ...")
    lines.append("")
    lines.append(
        "بعد از تاچ شدن TP1 پوزیشن روی نقطه ورود ریسک فری شود."
    )

    return "\n".join(lines)
    
    
    
def communities_reply_keyboard(market, selected_names=None):
    selected_names = selected_names or []

    communities = get_market_communities(market)

    keyboard = []

    for community in communities:
        name = community["name"]

        checked = "✅" if name in selected_names else "⬜️"

        keyboard.append([
            f"{checked} {name}"
        ])

    keyboard.append([
        "📣 ارسال به همه کامیونیتی‌ها"
    ])

    keyboard.append([
        "🚀 ارسال به انتخاب‌شده‌ها"
    ])

    keyboard.append([
        "🔙 بازگشت"
    ])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# =========================================================
# CHANNEL HEALTH CHECK
# =========================================================

async def check_channels_health(bot, chat_ids):
    """
    بررسی دسترسی بات به کانال‌ها قبل از ارسال سیگنال.

    خروجی:
        (healthy_ids, failed_ids)
    """
    healthy = []
    failed = []

    for chat_id in chat_ids:
        try:
            await bot.get_chat(chat_id)
            healthy.append(chat_id)
        except Exception:
            failed.append(chat_id)

    return healthy, failed