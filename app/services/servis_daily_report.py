# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.services import servis_report_manager as report_manager

from app.settings.config import (
    ADMIN_ID,
    DAILY_REPORT_HOUR,
    DAILY_REPORT_MINUTE,
    DAILY_REPORT_TIMEZONE,
)


# =========================================================
# DAILY REPORT JOB
# =========================================================
async def send_daily_reports(context):

    timezone = DAILY_REPORT_TIMEZONE

    now = datetime.now(timezone)

    # =========================================================
    # بازه گزارش: 24 ساعت قبل تا همین لحظه
    # =========================================================

    start_time = now - timedelta(hours=24)
    end_time = now

    print(
        f"DAILY REPORT | FROM: {start_time}"
    )

    print(
        f"DAILY REPORT | TO: {end_time}"
    )

    # =========================================================
    # LOAD LOGS
    # =========================================================

    logs = report_manager.load_logs()

    # =========================================================
    # FILTER BY EXACT 24-HOUR WINDOW
    # =========================================================

    filtered_logs = []

    for log in logs:

        try:
            log_dt = datetime.strptime(
                log["date"],
                "%Y-%m-%d %H:%M:%S"
            )
            log_dt = log_dt.replace(
                tzinfo=timezone
            )

        except (KeyError, ValueError):
            continue

        if start_time <= log_dt < end_time:
            filtered_logs.append(log)

    print(
        f"DAILY REPORT | TOTAL SIGNALS: {len(filtered_logs)}"
    )

    # =========================================================
    # FOREX
    # =========================================================

    forex_logs = [
        log
        for log in filtered_logs
        if log.get("market") == "forex"
    ]

    # =========================================================
    # CRYPTO
    # =========================================================

    crypto_logs = [
        log
        for log in filtered_logs
        if log.get("market") == "crypto"
    ]

    print(
        f"DAILY REPORT | FOREX: {len(forex_logs)}"
    )

    print(
        f"DAILY REPORT | CRYPTO: {len(crypto_logs)}"
    )

    # =========================================================
    # FILES
    # =========================================================

    forex_file = (
        report_manager.export_to_excel(
            forex_logs,
            report_manager.DATA_DIR
            / f"daily_report_forex_{now.strftime('%Y-%m-%d_%H-%M')}.xlsx"
        )
    )

    crypto_file = (
        report_manager.export_to_excel(
            crypto_logs,
            report_manager.DATA_DIR
            / f"daily_report_crypto_{now.strftime('%Y-%m-%d_%H-%M')}.xlsx"
        )
    )

    # =========================================================
    # SEND FOREX
    # =========================================================

    try:

        with open(
            forex_file,
            "rb"
        ) as f:

            await context.application.bot.send_document(
                chat_id=ADMIN_ID,
                document=f,
                caption=(
                    "📊 گزارش ۲۴ ساعته فارکس\n\n"
                    f"🕐 از: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"🕐 تا: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"📈 تعداد سیگنال‌ها: {len(forex_logs)}"
                )
            )

        print(
            "DAILY REPORT | FOREX SENT"
        )

    except Exception as e:

        print(
            f"DAILY REPORT | FOREX ERROR: {e}"
        )

    # =========================================================
    # SEND CRYPTO
    # =========================================================

    try:

        with open(
            crypto_file,
            "rb"
        ) as f:

            await context.application.bot.send_document(
                chat_id=ADMIN_ID,
                document=f,
                caption=(
                    "📊 گزارش ۲۴ ساعته کریپتو\n\n"
                    f"🕐 از: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"🕐 تا: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"🪙 تعداد سیگنال‌ها: {len(crypto_logs)}"
                )
            )

        print(
            "DAILY REPORT | CRYPTO SENT"
        )

    except Exception as e:

        print(
            f"DAILY REPORT | CRYPTO ERROR: {e}"
        )

    # =========================================================
    # CLEAN OLD EXCEL FILES
    # =========================================================

    report_manager.cleanup_old_daily_reports(
        days=30
    )
