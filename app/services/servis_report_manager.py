# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from openpyxl import Workbook
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from app.settings.config import (
    SIGNAL_LOG_FILE,
    DATA_DIR,
)


# =========================================================
# LOAD / SAVE LOGS
# =========================================================

def load_logs():

    if not SIGNAL_LOG_FILE.exists():
        return []

    try:

        with open(
            SIGNAL_LOG_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read().strip()

            return json.loads(content) if content else []

    except (json.JSONDecodeError, OSError):

        return []


def save_logs(logs):

    DATA_DIR.mkdir(
        parents=True,
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


# =========================================================
# FILTERS
# =========================================================

def filter_by_time(
    logs,
    months: int | None = None,
    years: int | None = None
):

    now = datetime.now()

    result = []

    for log in logs:

        try:

            dt = datetime.strptime(
                log["date"],
                "%Y-%m-%d %H:%M:%S"
            )

        except (KeyError, ValueError):

            continue

        if months is not None:

            if dt >= now - timedelta(
                days=30 * months
            ):

                result.append(log)

        elif years is not None:

            if dt >= now - timedelta(
                days=365 * years
            ):

                result.append(log)

    return result


def filter_by_channels(logs, channel_ids):

    return [
        l
        for l in logs
        if any(
            ch in l.get("channels", [])
            for ch in channel_ids
        )
    ]


# =========================================================
# FILTER BY MARKET
# =========================================================

def filter_by_market(logs, market):

    return [
        log
        for log in logs
        if log.get("market") == market
    ]


# =========================================================
# FILTER DAILY
# =========================================================

def filter_by_date(logs, target_date):

    result = []

    for log in logs:

        try:

            dt = datetime.strptime(
                log["date"],
                "%Y-%m-%d %H:%M:%S"
            )

        except (KeyError, ValueError):

            continue

        if dt.date() == target_date:

            result.append(log)

    return result


# =========================================================
# RESULT NAME
# =========================================================

def get_result_name(status):

    if status == "active":
        return "Active"

    elif status == "cancel":
        return "Cancel"

    elif status == "sl":
        return "SL"

    elif status == "exit":
        return "Exit"

    elif status == "be":
        return "Break Even"

    elif status == "full_tp":
        return "🏆 Full Target Hit"

    elif status.startswith("tp"):
        return status.upper()

    return status


# =========================================================
# EXPORT EXCEL
# =========================================================

def export_to_excel(logs, filename):

    filename = Path(filename)

    filename.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    wb = Workbook()

    ws = wb.active

    ws.title = "Reports"

    headers = [
        "Market",
        "Signal ID",
        "Symbol",
        "Position",
        "Leverage",
        "OrderType",
        "Entries",
        "SL",
        "TPs",
        "Result",
        "Communities",
        "Channels",
        "Date"
    ]

    ws.append(headers)

    for l in logs:

        status = l.get(
            "status",
            "active"
        )

        result = get_result_name(status)

        ws.append([
            l.get("market", ""),
            l.get("signal_id", ""),
            l.get("symbol", ""),
            l.get("position", ""),
            l.get("leverage", ""),
            l.get("order_type", ""),
            ",".join(
                str(x)
                for x in l.get("entries", [])
            ),
            l.get("sl", ""),
            ",".join(
                str(x)
                for x in l.get("tps", [])
            ),
            result,
            ",".join(
                str(x)
                for x in l.get("communities", [])
            ),
            ",".join(
                str(x)
                for x in l.get("channels", [])
            ),
            l.get("date", "")
        ])

    wb.save(filename)

    return str(filename)


# =========================================================
# DAILY REPORT
# =========================================================

def create_daily_report(
    market,
    target_date
):

    logs = load_logs()

    # اول تاریخ
    logs = filter_by_date(
        logs,
        target_date
    )

    # بعد بازار
    logs = filter_by_market(
        logs,
        market
    )

    market_name = (
        "forex"
        if market == "forex"
        else "crypto"
    )

    filename = (
        DATA_DIR
        / f"daily_report_{market_name}_{target_date.strftime('%Y-%m-%d')}.xlsx"
    )

    return export_to_excel(
        logs,
        filename
    )


# =========================================================
# CLEAN OLD DAILY REPORT FILES
# =========================================================

def cleanup_old_daily_reports(days=30):

    if not DATA_DIR.exists():
        return

    cutoff = datetime.now() - timedelta(
        days=days
    )

    for file in DATA_DIR.glob(
        "daily_report_*.xlsx"
    ):

        try:

            if datetime.fromtimestamp(
                file.stat().st_mtime
            ) < cutoff:

                file.unlink()

        except OSError:

            pass


# =========================================================
# OLD REPORT CLEANUP
# =========================================================

def delete_old_reports(channel_ids):

    logs = load_logs()

    now = datetime.now()

    new_logs = []

    for log in logs:

        try:

            dt = datetime.strptime(
                log["date"],
                "%Y-%m-%d %H:%M:%S"
            )

        except (KeyError, ValueError):

            continue

        if any(
            ch in log.get("channels", [])
            for ch in channel_ids
        ):

            if dt >= now - timedelta(
                days=30
            ):

                new_logs.append(log)

        else:

            new_logs.append(log)

    save_logs(new_logs)


# =========================================================
# REPORT CHANNEL KEYBOARD
# =========================================================

def report_channels_keyboard(
    channels,
    selected_ids
):

    buttons = []

    for ch in channels:

        chat_id = ch["chat_id"]

        title = (
            ch.get("title")
            or str(chat_id)
        )

        checked = (
            "✅"
            if chat_id in selected_ids
            else "⬜"
        )

        buttons.append([
            InlineKeyboardButton(
                f"{checked} {title}",
                callback_data=(
                    f"toggle_report_channel:{chat_id}"
                )
            )
        ])

    # -----------------------------------------------------
    # REPORT SELECTED
    # -----------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "📊 گزارش کانال‌های انتخاب‌شده",
            callback_data="report_send_selected"
        )
    ])

    # -----------------------------------------------------
    # REPORT ALL MARKET CHANNELS
    # -----------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "🌐 گزارش همه کانال‌های این بازار",
            callback_data="report_all_channels"
        )
    ])

    # -----------------------------------------------------
    # CANCEL
    # -----------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "❌ لغو",
            callback_data="report_cancel"
        )
    ])

    return InlineKeyboardMarkup(buttons)

    
# =========================================================
# MARKET KEYBOARD
# =========================================================

def report_market_keyboard():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🪙 کریپتو",
                callback_data="report_market:crypto"
            )
        ],

        [
            InlineKeyboardButton(
                "📈 فارکس",
                callback_data="report_market:forex"
            )
        ],

        [
            InlineKeyboardButton(
                "🌐 همه موارد",
                callback_data="report_market:all"
            )
        ],

        [
            InlineKeyboardButton(
                "❌ لغو",
                callback_data="report_cancel"
            )
        ]
    ])

    
# =========================================================
# TIME KEYBOARD
# =========================================================

def report_time_keyboard():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "📅 یک ماه",
                callback_data="report_time:1m"
            )
        ],

        [
            InlineKeyboardButton(
                "📅 سه ماه",
                callback_data="report_time:3m"
            )
        ],

        [
            InlineKeyboardButton(
                "📅 شش ماه",
                callback_data="report_time:6m"
            )
        ],

        [
            InlineKeyboardButton(
                "📅 یک سال",
                callback_data="report_time:1y"
            )
        ],

        [
            InlineKeyboardButton(
                "❌ لغو",
                callback_data="report_cancel"
            )
        ]
    ])

    
    
    
    
    
    
    
    
    
    