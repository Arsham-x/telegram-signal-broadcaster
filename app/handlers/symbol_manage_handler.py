# -*- coding: utf-8 -*-

from telegram import Update
from telegram.ext import ContextTypes

from app.services import servis_symbol_manager as symbol_manager


async def handle_symbol_manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = (update.message.text or "").strip()

    # ================== مدیریت نمادها ==================

    if text == "🪙 اد نماد":
        context.user_data["symbol_flow"] = True
        context.user_data["symbol_category"] = None
        context.user_data["symbol_action"] = None
        context.user_data["symbol_page"] = 0

        await update.message.reply_text(
            "بازار را انتخاب کن:",
            reply_markup=symbol_manager.category_keyboard()
        )

        return True

    # =========================================================
    # SYMBOL CATEGORY
    # =========================================================

    if (
        text in ["📈 فارکس", "🪙 کریپتو"]
        and context.user_data.get("symbol_flow") is True
        and context.user_data.get("symbol_category") is None
    ):

        if text == "🪙 کریپتو":
            category = "crypto"
        else:
            category = "forex"

        context.user_data["symbol_category"] = category

        await update.message.reply_text(
            f"دسته انتخاب شد: {text}",
            reply_markup=symbol_manager.symbol_action_keyboard()
        )

        return True

    # ================== انتخاب عملیات ==================

    if text in [
        "➕ افزودن نماد",
        "🗑 حذف نماد",
        "📋 لیست نمادها"
    ]:

        category = context.user_data.get(
            "symbol_category"
        )

        if not category:

            await update.message.reply_text(
                "اول دسته را انتخاب کن."
            )

            return True

        # ---------------- افزودن ----------------

        if text == "➕ افزودن نماد":

            context.user_data["symbol_action"] = "add"

            await update.message.reply_text(
                "نام نماد را وارد کن:"
            )

            return True

        # ---------------- حذف ----------------

        if text == "🗑 حذف نماد":

            context.user_data["symbol_action"] = "delete"

            symbols = symbol_manager.get_symbols(
                category
            )

            if not symbols:

                await update.message.reply_text(
                    "در این دسته نمادی وجود ندارد."
                )

                return True

            await update.message.reply_text(
                f"نمادهای {category} برای حذف:",
                reply_markup=symbol_manager.symbols_keyboard(
                    symbols
                )
            )

            return True

        # ---------------- لیست ----------------

        if text == "📋 لیست نمادها":

            symbols = symbol_manager.get_symbols(
                category
            )

            if not symbols:

                await update.message.reply_text(
                    "لیست این دسته خالی است."
                )

                return True

            title = (
                "کریپتو"
                if category == "crypto"
                else "فارکس"
            )

            await update.message.reply_text(
                f"📋 لیست نمادهای {title}:\n\n"
                + "\n".join(symbols),
                reply_markup=symbol_manager.symbol_action_keyboard()
            )

            return True

    # ================== انجام عملیات روی نماد ==================

    if context.user_data.get("symbol_action"):

        category = context.user_data.get(
            "symbol_category"
        )

        action = context.user_data.get(
            "symbol_action"
        )

        # ---------------- افزودن ----------------

        if action == "add":

            symbol_manager.add_symbol(
                category,
                text
            )

            context.application.bot_data["symbols"] = (
                symbol_manager.load_symbols()
            )

            await update.message.reply_text(
                "✅ نماد اضافه شد.",
                reply_markup=symbol_manager.symbol_action_keyboard()
            )

            context.user_data["symbol_action"] = None

            return True

        # ---------------- حذف ----------------

        if action == "delete":

            symbol_manager.remove_symbol(
                category,
                text
            )

            context.application.bot_data["symbols"] = (
                symbol_manager.load_symbols()
            )

            await update.message.reply_text(
                "🗑 نماد حذف شد.",
                reply_markup=symbol_manager.symbol_action_keyboard()
            )

            context.user_data["symbol_action"] = None

            return True

    return False