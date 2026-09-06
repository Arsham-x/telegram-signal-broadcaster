from telegram import Update
from telegram.ext import ContextTypes

from app.services import servis_report_manager as report_manager


async def handle_report(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = (update.message.text or "").strip()

    # ================== شروع گزارش گیری ==================

    if text == "📊 گزارش گیری":

        # ریست وضعیت قبلی گزارش
        context.user_data["report_market"] = None
        context.user_data["report_selected_channels"] = []
        context.user_data["report_all_market"] = False

        await update.message.reply_text(
            "📊 گزارش برای کدام بازار است؟",
            reply_markup=report_manager.report_market_keyboard()
        )

        return True

    return False
