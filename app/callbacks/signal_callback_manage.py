# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ContextTypes

import json
import asyncio

from app.services import servis_signal_control as signal_control


def _write_signal_logs_sync(logs):
    """نوشتن لاگ سیگنال‌ها — sync، داخل thread اجرا میشه."""
    with open(
        signal_control.SIGNAL_LOG_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            logs,
            f,
            ensure_ascii=False,
            indent=2
        )


async def signal_manage_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    data = query.data

    logs = signal_control.load_signal_logs()
    texts = signal_control.load_signal_texts()

    # =========================================================
    # HIDE SIGNAL FROM MANAGEMENT LIST
    # =========================================================

    if data == "signal_hide_mode":

        context.user_data["waiting_for_signal_hide_id"] = True

        await query.message.reply_text(
            "شماره سیگنالی که می‌خواهی از لیست مدیریت حذف شود را ارسال کن:"
        )

        return

    # =========================================================
    # SELECT SIGNAL
    # =========================================================

    if data.startswith("manage_signal:"):

        index = int(data.split(":")[1])

        await query.message.reply_text(
            "وضعیت سیگنال:",
            reply_markup=signal_control.signal_manage_keyboard(
                index
            )
        )

        return

    # =========================================================
    # ACTIVE
    # =========================================================

    if data.startswith("signal_active:"):

        index = int(data.split(":")[1])

        signal = logs[index]

        text = texts.get(
            "active",
            "✅ پوزیشن فعال شد. مدیریت ریسک رعایت شود."
        )

        for ch_id in signal.get("channels", []):

            reply_id = signal.get(
                "message_ids",
                {}
            ).get(
                str(ch_id)
            )

            try:

                await context.application.bot.send_message(
                    chat_id=ch_id,
                    text=text,
                    parse_mode="HTML",
                    reply_to_message_id=reply_id
                )

            except Exception as e:

                print("FAILED ACTIVE:", ch_id)
                print(str(e))

        await query.message.reply_text(
            "✅ پوزیشن فعال شد."
        )

        return

    # =========================================================
    # DEACTIVE
    # =========================================================

    if data.startswith("signal_deactive:"):

        index = int(
            data.split(":")[1]
        )

        await query.message.reply_text(
            "دلیل غیرفعال شدن رو انتخاب کن:",
            reply_markup=signal_control.signal_deactive_reasons_keyboard(
                index
            )
        )

        return

    # =========================================================
    # TP
    # =========================================================

    if data.startswith("signal_tp:"):

        _, index, tp_number = data.split(":")

        index = int(index)
        tp_number = int(tp_number)

        signal = logs[index]

        tp_count = len(
            signal.get("tps", [])
        )

        # -----------------------------------------------------
        # متن TP
        # -----------------------------------------------------

        if tp_number == tp_count:

            text = (
                f"🎯 TP{tp_number} حد سود فعال شد.\n\n"
                "🎯 فول سود شد."
            )

        else:

            text = texts.get(
                f"tp{tp_number}",
                f"🎯 TP{tp_number} حد سود فعال شد."
            )

        # -----------------------------------------------------
        # ارسال به کانال‌ها
        # -----------------------------------------------------

        for ch_id in signal.get("channels", []):

            reply_id = signal.get(
                "message_ids",
                {}
            ).get(
                str(ch_id)
            )

            try:

                await context.application.bot.send_message(
                    chat_id=ch_id,
                    text=text,
                    parse_mode="HTML",
                    reply_to_message_id=reply_id
                )

            except Exception as e:

                print("FAILED TP:", ch_id)
                print(str(e))

        # -----------------------------------------------------
        # ذخیره وضعیت
        # -----------------------------------------------------

        if tp_number == tp_count:

            signal["status"] = "full_tp"

        else:

            signal["status"] = f"tp{tp_number}"

        await asyncio.to_thread(_write_signal_logs_sync, logs)

        await query.message.reply_text(
            f"✅ TP{tp_number} ارسال شد."
        )

        return

    # =========================================================
    # SIGNAL REASON
    # =========================================================

    if data.startswith("signal_reason:"):

        _, reason, index = data.split(":")

        index = int(index)

        signal = logs[index]

        # =====================================================
        # TP MENU
        # =====================================================

        if reason == "tp":

            tp_count = len(
                signal.get("tps", [])
            )

            await query.message.reply_text(
                "🎯 کدام حد سود تاچ شد؟",
                reply_markup=signal_control.signal_tp_keyboard(
                    index,
                    tp_count
                )
            )

            return

        # =====================================================
        # متن هر وضعیت
        # =====================================================

        reason_texts = {

            "cancel":
                "❌ این سیگنال کنسل شد.",

            "sl":
                "🛑 حد ضرر فعال شد.",

            "exit":
                "🚪 خروج فوری از پوزیشن انجام شود.",

            "be":
                "🟡 حد ضرر روی نقطه ورود (Break Even) تنظیم شود."
        }
        text = texts.get(
            reason
        )

        if not text:

            text = reason_texts.get(
                reason,
                "⚠️ وضعیت سیگنال مشخص نیست."
            )

        # =====================================================
        # ذخیره وضعیت
        # =====================================================

        signal["status"] = reason

        await asyncio.to_thread(_write_signal_logs_sync, logs)

        # =====================================================
        # ارسال متن واقعی وضعیت به کانال
        # =====================================================

        for ch_id in signal.get("channels", []):

            reply_id = signal.get(
                "message_ids",
                {}
            ).get(
                str(ch_id)
            )

            try:

                await context.application.bot.send_message(
                    chat_id=ch_id,
                    text=text,
                    parse_mode="HTML",
                    reply_to_message_id=reply_id
                )

            except Exception as e:

                print(
                    "FAILED SIGNAL STATUS:",
                    ch_id
                )

                print(
                    "REASON:",
                    reason
                )

                print(
                    "TEXT:",
                    text
                )

                print(
                    str(e)
                )

        # =====================================================
        # پیام تأیید برای ادمین
        # =====================================================

        admin_messages = {

            "cancel":
                "❌ سیگنال کنسل شد.",

            "sl":
                "🛑 حد ضرر فعال شد.",

            "exit":
                "🚪 خروج فوری انجام شد.",

            "be":
                "🟡 بریک ایون انجام شد."
        }

        admin_text = admin_messages.get(
            reason,
            "✅ وضعیت سیگنال به‌روزرسانی شد."
        )

        await query.message.reply_text(
            admin_text
        )

        return

