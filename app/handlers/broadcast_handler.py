# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ContextTypes

from app.services import servis_broadcast_manager as broadcast_manager


async def handle_broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = (update.message.text or "").strip()


    # =========================================================
    # شروع ارسال پیام همگانی
    # =========================================================

    if text == "📣 ارسال پیام همگانی":

        await broadcast_manager.start_broadcast_flow(
            update,
            context
        )

        return True


    # =========================================================
    # ادامه Flow ارسال پیام همگانی
    # =========================================================

    handled = await broadcast_manager.handle_broadcast_message(
        update,
        context
    )

    if handled:
        return True


    # =========================================================
    # این Handler این پیام را مدیریت نکرد
    # =========================================================

    return False

