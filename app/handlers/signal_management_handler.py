import json
import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from app.services import servis_signal_control as signal_control


async def handle_signal_management(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = (update.message.text or "").strip()

    # =========================================================
    # شروع مدیریت سیگنال
    # =========================================================

    if text == "⚙️ مدیریت سیگنال":

        context.user_data["signal_management_mode"] = True
        context.user_data["signal_management_market"] = None

        await update.message.reply_text(
            "سیگنال‌های کدام بازار را می‌خواهی مدیریت کنی؟",
            reply_markup=signal_control.signal_market_keyboard()
        )

        return True

    # =========================================================
    # انتخاب بازار در مدیریت سیگنال
    # =========================================================

    if context.user_data.get("signal_management_mode"):

        market_map = {
            "📈 فارکس": "forex",
            "🪙 کریپتو": "crypto"
        }

        if text in market_map:

            market = market_map[text]

            context.user_data["signal_management_market"] = market

            logs = signal_control.load_signal_logs()

            active_logs = []

            for real_index, log in enumerate(logs):

                # فقط بازار انتخاب‌شده
                if log.get("market") != market:
                    continue

                # سیگنال‌های بسته‌شده نمایش داده نشوند
                if log.get("status", "active") in [
                    "cancel",
                    "sl",
                    "exit",
                    "full_tp"
                ]:
                    continue

                if log.get("hidden_from_management", False):
                    continue
                log["_real_index"] = real_index

                active_logs.append(log)

            if not active_logs:

                market_name = (
                    "فارکس"
                    if market == "forex"
                    else "کریپتو"
                )

                await update.message.reply_text(
                    f"هیچ سیگنال فعالی در بازار {market_name} وجود ندارد."
                )

                return True

            await update.message.reply_text(
                "یکی از سیگنال‌ها را انتخاب کن:",
                reply_markup=signal_control.signal_list_keyboard(
                    active_logs
                )
            )

            return True

    # =========================================================
    # حذف سیگنال از لیست مدیریت
    # =========================================================

    if context.user_data.get("waiting_for_signal_hide_id"):

        try:
            signal_id = int(text)

        except ValueError:

            await update.message.reply_text(
                "❌ شماره سیگنال باید عدد باشد.\n"
                "مثلاً: 12"
            )

            return True

        market = context.user_data.get(
            "signal_management_market"
        )

        if not market:

            context.user_data[
                "waiting_for_signal_hide_id"
            ] = False

            await update.message.reply_text(
                "❌ بازار انتخاب نشده. "
                "دوباره وارد مدیریت سیگنال شو."
            )

            return True

        logs = signal_control.load_signal_logs()

        found = False

        for log in logs:

            if log.get("signal_id") != signal_id:
                continue

            if log.get("market") != market:
                continue

            log["hidden_from_management"] = True

            found = True
            break

        if not found:

            market_name = (
                "فارکس"
                if market == "forex"
                else "کریپتو"
            )

            await update.message.reply_text(
                f"❌ سیگنال شماره {signal_id} "
                f"در لیست {market_name} پیدا نشد."
            )

            return True

        # =====================================================
        # ذخیره تغییرات
        # =====================================================

        def _write():
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

        await asyncio.to_thread(_write)

        context.user_data[
            "waiting_for_signal_hide_id"
        ] = False

        await update.message.reply_text(
            f"✅ سیگنال شماره {signal_id} "
            "از لیست مدیریت حذف شد.\n\n"
            "رکورد سیگنال در دیتابیس باقی ماند."
        )

        return True

    # =========================================================
    # این پیام مربوط به این Handler نبود
    # =========================================================

    return False
