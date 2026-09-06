# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ContextTypes
from app.services import servis_reply_manager as reply_manager
from app.services import servis_signal_control as signal_control
async def reply_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("reply_delete:"):

        index = int(data.split(":")[1])

        texts = reply_manager.load_reply_texts()

        if index >= len(texts):
            await query.answer("وجود ندارد.", show_alert=True)
            return

        texts.pop(index)

        reply_manager.save_reply_texts(texts)

        if texts:
            await query.edit_message_reply_markup(
                reply_markup=reply_manager.reply_texts_inline_keyboard(texts)
            )
        else:
            await query.edit_message_text("همه جملات حذف شدند.")

        await query.answer("✅ حذف شد")

    if query.data.startswith("reply_signal:"):

        index = int(query.data.split(":")[1])

        context.user_data["selected_reply_signal"] = index
        print("SELECTED SIGNAL:", index)

        texts = reply_manager.load_reply_texts()

        if not texts:
            await query.message.reply_text("هیچ جمله آماده‌ای ثبت نشده است.")
            return

        await query.message.reply_text(
            "جمله موردنظر را انتخاب کن:",
            reply_markup=reply_manager.reply_saved_texts_keyboard(texts)
        )
        return
    if query.data.startswith("reply_send:"):

        text_index = int(query.data.split(":")[1])

        texts = reply_manager.load_reply_texts()

        if text_index >= len(texts):
            await query.answer("جمله پیدا نشد.", show_alert=True)
            return

        reply_text = texts[text_index]

        signal_index = context.user_data.get("selected_reply_signal")

        if signal_index is None:
            await query.answer("سیگنال انتخاب نشده.", show_alert=True)
            return

        logs = signal_control.load_signal_logs()

        signal = logs[signal_index]
        for ch_id in signal["channels"]:

            reply_id = signal.get("message_ids", {}).get(str(ch_id))

            if not reply_id:
                continue

            try:
                await context.application.bot.send_message(
                    chat_id=ch_id,
                    text=reply_text,
                    reply_to_message_id=reply_id
                )
            except Exception as e:
                print("SEND REPLY TO:", ch_id)
                print("REPLY ID:", reply_id)
                

        await query.message.reply_text("✅ پیام ارسال شد.")
        return

    if query.data.startswith("reply_manual_signal:"):

        index = int(query.data.split(":")[1])

        context.user_data["selected_reply_signal"] = index
        context.user_data["waiting_manual_reply"] = True

        await query.message.reply_text(
            "✍️ متن موردنظر را ارسال کن:"
        )
        return
