# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup

from app.services import servis_signal_manager as signal_manager
from app.services import servis_keyboard as keyboard_service

BACK_TEXT = "⬅️ یک مرحله قبل"


def _with_back(markup):
    """
    دکمه «یک مرحله قبل» را قبل از «بازگشت» قرار می‌دهد.
    «🔙 بازگشت» از کیبورد اصلی حفظ می‌شود.
    """

    if markup is None:
        return ReplyKeyboardMarkup(
            [
                [BACK_TEXT],
                ["🔙 بازگشت"]
            ],
            resize_keyboard=True
        )

    rows = [
        [
            item
            for item in row
            if item != BACK_TEXT
        ]
        for row in markup.keyboard
    ]

    rows = [row for row in rows if row]

    has_global_back = False
    new_rows = []

    for row in rows:
        if "🔙 بازگشت" in row:
            has_global_back = True
            row = [item for item in row if item != "🔙 بازگشت"]

        if row:
            new_rows.append(row)

    new_rows.append([BACK_TEXT])

    if has_global_back:
        new_rows.append(["🔙 بازگشت"])

    return ReplyKeyboardMarkup(
        new_rows,
        resize_keyboard=True
    )


def _symbols_keyboard(page, symbols):
    """کیبورد نمادها + بازگشت ثابت."""
    return _with_back(
        keyboard_service.paginated_symbols_keyboard(page, symbols)
    )


def _market_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["🪙 کریپتو", "📈 فارکس"],
            ["🔙 بازگشت"],
        ],
        resize_keyboard=True,
    )


async def _show_market(update):
    await update.message.reply_text(
        "بازار را انتخاب کن:",
        reply_markup=_market_keyboard(),
    )


async def _show_symbols(update, context, symbols, page=0):
    context.user_data["waiting_for_signal_market"] = False
    context.user_data["waiting_for_signal_symbol"] = True
    context.user_data["waiting_for_signal_flow"] = False
    context.user_data["symbol_page"] = page

    await update.message.reply_text(
        "یک نماد انتخاب کنید:",
        reply_markup=_symbols_keyboard(page, symbols),
    )


async def _show_position(update, data):
    await update.message.reply_text(
        "پوزیشن را انتخاب کن:",
        reply_markup=_with_back(
            signal_manager.position_keyboard(data["market"])
        ),
    )


async def _show_order_type(update):
    await update.message.reply_text(
        "نوع ورود را انتخاب کن:",
        reply_markup=_with_back(signal_manager.order_type_keyboard()),
    )


async def _show_entry(update, number):
    await update.message.reply_text(
        f"Entry {number} را وارد کن:",
        reply_markup=_with_back(signal_manager.back_keyboard()),
    )


async def _show_sl(update):
    await update.message.reply_text(
        "حد ضرر (SL) را وارد کن:",
        reply_markup=_with_back(signal_manager.back_keyboard()),
    )


async def _show_tp(update):
    await update.message.reply_text(
        "TP را وارد کن:",
        reply_markup=_with_back(signal_manager.tp_keyboard()),
    )


async def _exit_signal_creation(update, context, user_id):
    """خروج کامل از ساخت سیگنال؛ بازگشت کلی برنامه حذف نمی‌شود."""
    signal_manager.clear_signal_session(context, user_id)
    await update.message.reply_text("از ساخت سیگنال خارج شدی.")


async def handle_signal_manage(update, context):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()

    signal_data = context.user_data.get("signal", {})
    data = signal_data.get(user_id)

    # =========================================================
    # شروع سیگنال جدید
    # =========================================================
    if text == "🚀 سیگنال جدید":
        signal_manager.clear_signal_session(context, user_id)

        context.user_data["waiting_for_signal_market"] = True
        context.user_data["waiting_for_signal_symbol"] = False
        context.user_data["waiting_for_signal_flow"] = False

        await _show_market(update)
        return

    # =========================================================
    # بازگشت مرحله‌ای
    # =========================================================
    if text == BACK_TEXT:
        if context.user_data.get("waiting_for_signal_market") and not data:
            await _exit_signal_creation(update, context, user_id)
            return

        if context.user_data.get("waiting_for_signal_symbol"):
            context.user_data.pop("signal_symbols", None)
            context.user_data.pop("symbol_page", None)

            if data:
                data["symbol"] = None
                data["position"] = None
                data["leverage"] = None
                data["order_type"] = None
                data["entries"] = []
                data["entry_done"] = False
                data["waiting_for_entry"] = False
                data["sl"] = None
                data["tps"] = []
                data["step"] = "market"

            context.user_data["waiting_for_signal_symbol"] = False
            context.user_data["waiting_for_signal_flow"] = False
            context.user_data["waiting_for_signal_market"] = True

            await _show_market(update)
            return

        if not data:
            await update.message.reply_text("سیگنال فعالی وجود ندارد.")
            return

        step = data.get("step")

        # -----------------------------------------------------
        # TP VALUE → TP MENU
        # -----------------------------------------------------
        if step == "tp_value":
            data["waiting_for_tp"] = False
            await _show_tp(update)
            data["step"] = "tp"
            return

        # -----------------------------------------------------
        # TP → SL
        # -----------------------------------------------------
        if step == "tp":
            data["tps"] = []
            data["waiting_for_tp"] = False
            data["step"] = "sl"
            await _show_sl(update)
            return

        # -----------------------------------------------------
        # SL → ORDER TYPE
        # -----------------------------------------------------
        if step == "sl":
            data["sl"] = None
            data["step"] = "order_type"
            await _show_order_type(update)
            return

        # -----------------------------------------------------
        # ENTRY VALUE → ORDER TYPE
        # -----------------------------------------------------
        if step == "entry_value":
            data["entries"] = []
            data["entry_done"] = False
            data["waiting_for_entry"] = False
            data["order_type"] = None
            data["step"] = "order_type"
            await _show_order_type(update)
            return

        # -----------------------------------------------------
        # ENTRY MENU → ORDER TYPE
        # -----------------------------------------------------
        if step == "entry":
            data["entries"] = []
            data["entry_done"] = False
            data["waiting_for_entry"] = False
            data["order_type"] = None
            data["step"] = "order_type"
            await _show_order_type(update)
            return

        # -----------------------------------------------------
        # ORDER TYPE → مرحله قبلی
        # Crypto: Leverage
        # Forex: Position
        # -----------------------------------------------------
        if step == "order_type":
            data["order_type"] = None
            data["entries"] = []
            data["entry_done"] = False
            data["waiting_for_entry"] = False

            if data.get("market") == "crypto":
                data["leverage"] = None
                data["step"] = "leverage"

                await update.message.reply_text(
                    "لوریج را وارد کن:",
                    reply_markup=_with_back(signal_manager.back_keyboard()),
                )
                return

            data["position"] = None
            data["step"] = "position"
            await _show_position(update, data)
            return

        # -----------------------------------------------------
        # LEVERAGE → POSITION
        # -----------------------------------------------------
        if step == "leverage":
            data["leverage"] = None
            data["position"] = None
            data["step"] = "position"
            await _show_position(update, data)
            return

        # -----------------------------------------------------
        # POSITION → SYMBOL
        # -----------------------------------------------------
        if step == "position":
            data["position"] = None
            if data.get("market") == "crypto":
                data["leverage"] = None

            context.user_data["waiting_for_signal_flow"] = False
            context.user_data["waiting_for_signal_symbol"] = True

            data["step"] = "symbol"

            await update.message.reply_text(
                "یک نماد انتخاب کنید:",
                reply_markup=_symbols_keyboard(
                    context.user_data.get("symbol_page", 0),
                    context.user_data.get("signal_symbols", []),
                ),
            )
            return

        # -----------------------------------------------------
        # SYMBOL / MARKET
        # اگر state به هر دلیل اینجا رسید، بازار نمایش داده شود.
        # -----------------------------------------------------
        if step == "symbol":
            data["symbol"] = None
            data["position"] = None
            data["leverage"] = None
            data["order_type"] = None
            data["entries"] = []
            data["entry_done"] = False
            data["waiting_for_entry"] = False
            data["sl"] = None
            data["tps"] = []
            data["step"] = "market"

            context.user_data["waiting_for_signal_flow"] = False
            context.user_data["waiting_for_signal_symbol"] = False
            context.user_data["waiting_for_signal_market"] = True

            await _show_market(update)
            return

        data["step"] = "market"
        context.user_data["waiting_for_signal_flow"] = False
        context.user_data["waiting_for_signal_symbol"] = False
        context.user_data["waiting_for_signal_market"] = True
        await _show_market(update)
        return

    # =========================================================
    # انتخاب بازار
    # =========================================================
    if context.user_data.get("waiting_for_signal_market"):
        if text == "🪙 کریپتو":
            market = "crypto"
        elif text == "📈 فارکس":
            market = "forex"
        else:
            await _show_market(update)
            return

        context.user_data["signal_market"] = market

        all_symbols = context.application.bot_data.get("symbols", {})
        if not isinstance(all_symbols, dict):
            await update.message.reply_text("خطا در اطلاعات نمادها.")
            return

        symbols = all_symbols.get(market, [])
        if not symbols:
            await update.message.reply_text(
                "برای این بازار هنوز هیچ نمادی ثبت نشده.",
                reply_markup=_market_keyboard(),
            )
            return

        context.user_data["signal_symbols"] = symbols
        context.user_data["symbol_page"] = 0

        await _show_symbols(update, context, symbols, 0)
        return

    # =========================================================
    # انتخاب نماد
    # =========================================================
    if context.user_data.get("waiting_for_signal_symbol"):
        symbols = context.user_data.get("signal_symbols", [])
        page = context.user_data.get("symbol_page", 0)

        if text == "➡️ بعدی":
            page += 1
            await update.message.reply_text(
                "صفحه بعد:",
                reply_markup=_symbols_keyboard(page, symbols),
            )
            context.user_data["symbol_page"] = page
            return

        if text == "⬅️ قبلی":
            page = max(0, page - 1)
            await update.message.reply_text(
                "صفحه قبل:",
                reply_markup=_symbols_keyboard(page, symbols),
            )
            context.user_data["symbol_page"] = page
            return

        if text not in symbols:
            await update.message.reply_text(
                "یک نماد انتخاب کنید:",
                reply_markup=_symbols_keyboard(page, symbols),
            )
            return

        signal_manager.reset_signal(user_id)
        context.user_data.setdefault("signal", {})
        context.user_data["signal"][user_id] = signal_manager.signal_state[user_id]

        data = context.user_data["signal"][user_id]
        data["symbol"] = text
        data["market"] = context.user_data["signal_market"]
        data["step"] = "position"

        context.user_data["waiting_for_signal_symbol"] = False
        context.user_data["waiting_for_signal_flow"] = True

        await _show_position(update, data)
        return

    # =========================================================
    # فلو ساخت سیگنال
    # =========================================================
    if context.user_data.get("waiting_for_signal_flow"):
        data = context.user_data.get("signal", {}).get(user_id)

        if not data:
            await update.message.reply_text("خطا در وضعیت سیگنال. دوباره شروع کن.")
            context.user_data["waiting_for_signal_flow"] = False
            return

        step = data.get("step")

        # =====================================================
        # POSITION
        # =====================================================
        if step == "position":
            if text not in ["SHORT", "LONG", "BUY", "SELL"]:
                await _show_position(update, data)
                return

            data["position"] = text

            if data["market"] == "crypto":
                data["step"] = "leverage"
                await update.message.reply_text(
                    "لوریج را وارد کن:",
                    reply_markup=_with_back(signal_manager.back_keyboard()),
                )
                return

            data["leverage"] = None
            data["step"] = "order_type"
            await _show_order_type(update)
            return

        # =====================================================
        # LEVERAGE - فقط CRYPTO
        # =====================================================
        if step == "leverage":
            if data["market"] != "crypto":
                data["step"] = "order_type"
                await _show_order_type(update)
                return

            if text.isdigit():
                data["leverage"] = text
                data["step"] = "order_type"
                await _show_order_type(update)
                return

            await update.message.reply_text(
                "لوریج باید عدد باشد.",
                reply_markup=_with_back(signal_manager.back_keyboard()),
            )
            return

        # =====================================================
        # ORDER TYPE
        # =====================================================
        if step == "order_type":
            if text == "مارکت":
                data["order_type"] = "MARKET"
                data["entries"] = ["Market"]
                data["entry_done"] = True
                data["waiting_for_entry"] = False
                data["step"] = "sl"
                await _show_sl(update)
                return

            if text == "تعیین حد":
                data["order_type"] = "LIMIT"
                data["entries"] = []
                data["waiting_for_entry"] = True
                data["entry_done"] = False
                data["step"] = "entry_value"
                await _show_entry(update, 1)
                return

            await _show_order_type(update)
            return

        # =====================================================
        # LIMIT ENTRY
        # =====================================================
        if data.get("order_type") == "LIMIT":
            if step == "entry_value" and data.get("waiting_for_entry"):
                data["entries"].append(text)
                data["waiting_for_entry"] = False
                data["step"] = "entry"

                await update.message.reply_text(
                    "✅ Entry ثبت شد.",
                    reply_markup=_with_back(signal_manager.entry_keyboard()),
                )
                return

            if step == "entry":
                if text == "➕ Entry اضافه":
                    data["waiting_for_entry"] = True
                    data["step"] = "entry_value"
                    await _show_entry(update, len(data["entries"]) + 1)
                    return

                if text == "✅ ادامه":
                    if not data["entries"]:
                        await _show_entry(update, 1)
                        return

                    data["entry_done"] = True
                    data["waiting_for_entry"] = False
                    data["step"] = "sl"
                    await _show_sl(update)
                    return

                return

        # =====================================================
        # SL
        # =====================================================
        if step == "sl":
            if not text:
                return

            data["sl"] = text
            data["tps"] = []
            data["waiting_for_tp"] = True
            data["step"] = "tp"
            await _show_tp(update)
            return

        # =====================================================
        # TP MENU / TP VALUE
        # =====================================================
        if step == "tp":
            if text == "➕ Tp اضافه":
                data["waiting_for_tp"] = True
                data["step"] = "tp_value"

                await update.message.reply_text(
                    f"Tp{len(data['tps']) + 1} را وارد کن:",
                    reply_markup=_with_back(signal_manager.back_keyboard()),
                )
                return

            if text == "✅ تمام":
                if not data["tps"]:
                    await update.message.reply_text(
                        "حداقل یک TP وارد کن ❗",
                        reply_markup=_with_back(signal_manager.tp_keyboard()),
                    )
                    return

                preview = signal_manager.build_signal_message_premium(data)

                await update.message.reply_text("👀 پیش‌نمایش پیام ارسالی:")
                await update.message.reply_text(
                    preview,
                    parse_mode="HTML",
                    reply_markup=signal_manager.signal_preview_keyboard(),
                )
                return

            return

        if step == "tp_value" and data.get("waiting_for_tp"):
            data["tps"].append(text)
            data["waiting_for_tp"] = False
            data["step"] = "tp"

            await update.message.reply_text(
                "TP اضافه شد ✅",
                reply_markup=_with_back(signal_manager.tp_keyboard()),
            )
            return

        await update.message.reply_text(
            "وضعیت مرحله نامشخص است. از بازگشت استفاده کن.",
            reply_markup=_with_back(signal_manager.back_keyboard()),
        )
