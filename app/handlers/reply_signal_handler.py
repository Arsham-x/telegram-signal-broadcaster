# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ContextTypes

from app.services import servis_reply_manager as reply_manager
from app.services import servis_signal_control as signal_control


async def handle_reply_signal(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = (update.message.text or "").strip()

    # =========================================================
    # شروع ریپلای به سیگنال
    # =========================================================

    if text == "💬 ریپلای به سیگنال":

        context.user_data["reply_flow"] = True

        context.user_data["reply_market"] = None
        context.user_data["reply_mode"] = None
        context.user_data["reply_manual_mode"] = False
        context.user_data["waiting_manual_reply"] = False
        context.user_data["selected_reply_signal"] = None

        await update.message.reply_text(
            "سیگنال مربوط به کدام بازار است؟",
            reply_markup=reply_manager.reply_market_keyboard()
        )

        return True


    # =========================================================
    # انتخاب بازار
    # =========================================================

    if (
        text in ["📈 فارکس", "🪙 کریپتو"]
        and context.user_data.get("reply_flow") is True
        and context.user_data.get("reply_market") is None
    ):

        market_map = {
            "📈 فارکس": "forex",
            "🪙 کریپتو": "crypto"
        }

        context.user_data["reply_market"] = market_map[text]

        await update.message.reply_text(
            f"بازار انتخاب شد: {text}\n\n"
            "حالا نوع پیام را انتخاب کن:",
            reply_markup=reply_manager.reply_menu_keyboard()
        )

        return True


    # =========================================================
    # مدیریت جملات آماده
    # =========================================================

    if text == "➕ جمله آماده":

        await update.message.reply_text(
            "مدیریت جملات:",
            reply_markup=reply_manager.reply_text_manage_keyboard()
        )

        return True


    if text == "➕ افزودن جمله":

        context.user_data["waiting_for_reply_text"] = True

        await update.message.reply_text(
            "جمله موردنظر را ارسال کن:"
        )

        return True


    if context.user_data.get("waiting_for_reply_text"):

        context.user_data["waiting_for_reply_text"] = False

        texts = reply_manager.load_reply_texts()

        texts.append(text)

        reply_manager.save_reply_texts(texts)

        await update.message.reply_text(
            "✅ جمله ذخیره شد.",
            reply_markup=reply_manager.reply_text_manage_keyboard()
        )

        return True


    if text == "🗂 مدیریت جملات":

        texts = reply_manager.load_reply_texts()

        if not texts:

            await update.message.reply_text(
                "هیچ جمله‌ای ثبت نشده است."
            )

            return True

        await update.message.reply_text(
            "برای حذف، روی جمله موردنظر بزن:",
            reply_markup=reply_manager.reply_texts_inline_keyboard(texts)
        )

        return True


    # =========================================================
    # پیام آماده
    # =========================================================

    if text == "📋 پیام آماده":

        market = context.user_data.get("reply_market")

        if not market:

            await update.message.reply_text(
                "❌ اول بازار را انتخاب کن."
            )

            return True


        all_logs = signal_control.load_signal_logs()

        logs = []

        for real_index, log in enumerate(all_logs):

            if log.get("market") != market:
                continue

            if log.get("status", "active") in [
                "cancel",
                "sl",
                "exit",
                "full_tp"
            ]:
                continue

            log["_real_index"] = real_index

            logs.append(log)


        if not logs:

            market_name = (
                "فارکس"
                if market == "forex"
                else "کریپتو"
            )

            await update.message.reply_text(
                f"هیچ سیگنال فعالی در بازار {market_name} وجود ندارد."
            )

            return True


        context.user_data["reply_mode"] = "saved"

        await update.message.reply_text(
            "سیگنال موردنظر را انتخاب کن:",
            reply_markup=reply_manager.reply_signal_keyboard(logs)
        )

        return True


    # =========================================================
    # پیام دستی
    # =========================================================

    if text == "⌨️ پیام دستی":

        market = context.user_data.get("reply_market")

        if not market:

            await update.message.reply_text(
                "❌ اول بازار را انتخاب کن."
            )

            return True


        all_logs = signal_control.load_signal_logs()

        logs = []

        for real_index, log in enumerate(all_logs):

            if log.get("market") != market:
                continue

            if log.get("status", "active") in [
                "cancel",
                "sl",
                "exit",
                "full_tp"
            ]:
                continue

            log["_real_index"] = real_index

            logs.append(log)


        if not logs:

            await update.message.reply_text(
                "هیچ سیگنال فعالی در این بازار وجود ندارد."
            )

            return True


        context.user_data["reply_manual_mode"] = True

        await update.message.reply_text(
            "سیگنال موردنظر را انتخاب کن:",
            reply_markup=reply_manager.reply_signal_keyboard(
                logs,
                prefix="reply_manual_signal"
            )
        )

        return True


    # =========================================================
    # دریافت پیام دستی و ارسال Reply به سیگنال
    # =========================================================

    if context.user_data.get("waiting_manual_reply"):

        context.user_data["waiting_manual_reply"] = False

        signal_index = context.user_data.get(
            "selected_reply_signal"
        )

        if signal_index is None:

            await update.message.reply_text(
                "❌ سیگنال انتخاب نشده."
            )

            return True


        logs = signal_control.load_signal_logs()

        if signal_index < 0 or signal_index >= len(logs):

            await update.message.reply_text(
                "❌ سیگنال پیدا نشد."
            )

            return True


        signal = logs[signal_index]

        message = update.message


        # =====================================================
        # تشخیص نوع پیام
        # =====================================================

        message_type = None
        file_id = None
        caption = message.caption


        if message.text:

            message_type = "text"


        elif message.photo:

            message_type = "photo"
            file_id = message.photo[-1].file_id


        elif message.voice:

            message_type = "voice"
            file_id = message.voice.file_id


        elif message.video:

            message_type = "video"
            file_id = message.video.file_id


        elif message.animation:

            message_type = "animation"
            file_id = message.animation.file_id


        elif message.audio:

            message_type = "audio"
            file_id = message.audio.file_id


        elif message.document:

            message_type = "document"
            file_id = message.document.file_id


        else:

            await update.message.reply_text(
                "❌ این نوع پیام فعلاً پشتیبانی نمی‌شود."
            )

            return True


        print(
            f"MANUAL REPLY | TYPE: {message_type} | "
            f"SIGNAL: {signal.get('symbol')}"
        )


        # =====================================================
        # ارسال به کانال‌های همان سیگنال
        # =====================================================

        success_count = 0
        failed_count = 0


        for ch_id in signal.get("channels", []):

            reply_id = (
                signal.get("message_ids", {})
                .get(str(ch_id))
            )


            if not reply_id:

                print(
                    f"NO REPLY MESSAGE ID | CHANNEL: {ch_id}"
                )

                continue


            try:

                if message_type == "text":

                    await context.application.bot.send_message(
                        chat_id=ch_id,
                        text=message.text,
                        reply_to_message_id=reply_id
                    )


                elif message_type == "photo":

                    await context.application.bot.send_photo(
                        chat_id=ch_id,
                        photo=file_id,
                        caption=caption,
                        reply_to_message_id=reply_id
                    )


                elif message_type == "voice":

                    await context.application.bot.send_voice(
                        chat_id=ch_id,
                        voice=file_id,
                        caption=caption,
                        reply_to_message_id=reply_id
                    )


                elif message_type == "video":

                    await context.application.bot.send_video(
                        chat_id=ch_id,
                        video=file_id,
                        caption=caption,
                        reply_to_message_id=reply_id
                    )


                elif message_type == "animation":

                    await context.application.bot.send_animation(
                        chat_id=ch_id,
                        animation=file_id,
                        caption=caption,
                        reply_to_message_id=reply_id
                    )


                elif message_type == "audio":

                    await context.application.bot.send_audio(
                        chat_id=ch_id,
                        audio=file_id,
                        caption=caption,
                        reply_to_message_id=reply_id
                    )


                elif message_type == "document":

                    await context.application.bot.send_document(
                        chat_id=ch_id,
                        document=file_id,
                        caption=caption,
                        reply_to_message_id=reply_id
                    )


                success_count += 1

                print(
                    f"REPLY SENT | CHANNEL: {ch_id} | "
                    f"REPLY ID: {reply_id}"
                )


            except Exception as e:

                failed_count += 1

                print(
                    f"FAILED REPLY | CHANNEL: {ch_id}"
                )

                print(
                    f"REPLY ID: {reply_id}"
                )

                print(
                    f"TYPE: {message_type}"
                )

                print(
                    f"ERROR: {e}"
                )


        # =====================================================
        # نتیجه
        # =====================================================

        await update.message.reply_text(
            f"✅ پیام ارسال شد.\n"
            f"نوع پیام: {message_type}\n"
            f"موفق: {success_count}\n"
            f"ناموفق: {failed_count}"
        )

        return True


    # =========================================================
    # این Handler این پیام را مدیریت نکرد
    # =========================================================

    return False