# -*- coding: utf-8 -*-
import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from app.services import servis_report_manager as report_manager
from app.services.servis_channel_manager import load_channels


# =========================================================
# CLEAR REPORT STATE
# =========================================================

def clear_report_state(context):

    context.user_data.pop(
        "report_market",
        None
    )

    context.user_data.pop(
        "report_selected_channels",
        None
    )

    context.user_data.pop(
        "report_all_market",
        None
    )


# =========================================================
# REPORT CALLBACK
# =========================================================

async def report_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data


    # =====================================================
    # CANCEL
    # =====================================================

    if data == "report_cancel":

        clear_report_state(context)

        await query.edit_message_text(
            "❌ گزارش‌گیری لغو شد."
        )

        return


    # =====================================================
    # MARKET SELECTION
    # =====================================================

    if data.startswith("report_market:"):

        market = data.split(
            ":",
            1
        )[1]

        context.user_data["report_market"] = market

        context.user_data[
            "report_selected_channels"
        ] = []


        # =================================================
        # ALL MARKETS
        # =================================================

        if market == "all":

            context.user_data[
                "report_all_market"
            ] = True

            await query.edit_message_text(

                "🌐 همه بازارها انتخاب شد.\n\n"
                "گزارش شامل تمام سیگنال‌ها خواهد بود.\n\n"
                "حالا بازه زمانی گزارش را انتخاب کن:",

                reply_markup=(
                    report_manager.report_time_keyboard()
                )
            )

            return


        # =================================================
        # SPECIFIC MARKET
        # =================================================

        context.user_data[
            "report_all_market"
        ] = False


        channels = load_channels()


        # -------------------------------------------------
        # فقط کانال‌های همان بازار
        # -------------------------------------------------

        market_channels = []

        for channel in channels:

            category = channel.get(
                "category"
            )

            if (
                category == market
                or category == "both"
            ):

                market_channels.append(
                    channel
                )


        # -------------------------------------------------
        # هیچ کانالی وجود ندارد
        # -------------------------------------------------

        if not market_channels:

            market_name = (
                "کریپتو"
                if market == "crypto"
                else "فارکس"
            )

            clear_report_state(
                context
            )

            await query.edit_message_text(

                f"❌ هیچ کانال یا گروهی برای "
                f"بازار {market_name} ثبت نشده است."
            )

            return


        market_name = (

            "🪙 کریپتو"
            if market == "crypto"
            else "📈 فارکس"
        )


        await query.edit_message_text(

            f"{market_name}\n\n"
            "کانال‌ها و گروه‌های این بازار را انتخاب کن:",

            reply_markup=(
                report_manager.report_channels_keyboard(
                    market_channels,
                    []
                )
            )
        )

        return


    # =====================================================
    # TOGGLE CHANNEL
    # =====================================================

    if data.startswith(
        "toggle_report_channel:"
    ):

        cid = int(
            data.split(
                ":",
                1
            )[1]
        )


        selected = context.user_data.setdefault(
            "report_selected_channels",
            []
        )


        # -------------------------------------------------
        # TOGGLE
        # -------------------------------------------------

        if cid in selected:

            selected.remove(cid)

        else:

            selected.append(cid)


        # -------------------------------------------------
        # بازار فعلی
        # -------------------------------------------------

        market = context.user_data.get(
            "report_market"
        )


        if market not in [
            "crypto",
            "forex"
        ]:

            await query.answer(
                "❌ بازار انتخاب نشده.",
                show_alert=True
            )

            return


        # -------------------------------------------------
        # دوباره کانال‌های همان بازار
        # -------------------------------------------------

        channels = load_channels()

        market_channels = []

        for channel in channels:

            category = channel.get(
                "category"
            )

            if (
                category == market
                or category == "both"
            ):

                market_channels.append(
                    channel
                )


        # -------------------------------------------------
        # آپدیت کیبورد
        # -------------------------------------------------

        await query.edit_message_reply_markup(

            reply_markup=(
                report_manager.report_channels_keyboard(
                    market_channels,
                    selected
                )
            )
        )

        return


    # =====================================================
    # REPORT ALL CHANNELS OF SELECTED MARKET
    # =====================================================

    if data == "report_all_channels":

        market = context.user_data.get(
            "report_market"
        )


        if market not in [
            "crypto",
            "forex"
        ]:

            await query.answer(
                "❌ بازار انتخاب نشده.",
                show_alert=True
            )

            return


        # -------------------------------------------------
        # هیچ فیلتر کانالی اعمال نمی‌شود
        # -------------------------------------------------

        context.user_data[
            "report_selected_channels"
        ] = []


        context.user_data[
            "report_all_market"
        ] = True


        market_name = (

            "🪙 کریپتو"
            if market == "crypto"
            else "📈 فارکس"
        )


        await query.edit_message_text(

            f"{market_name}\n\n"
            "📊 گزارش تمام سیگنال‌های این بازار "
            "برای تمام کانال‌ها و گروه‌های مربوط به "
            "این بازار تهیه می‌شود.\n\n"
            "حالا بازه زمانی گزارش را انتخاب کن:",

            reply_markup=(
                report_manager.report_time_keyboard()
            )
        )

        return


    # =====================================================
    # REPORT SELECTED CHANNELS
    # =====================================================

    if data == "report_send_selected":

        market = context.user_data.get(
            "report_market"
        )


        selected = context.user_data.get(
            "report_selected_channels",
            []
        )


        if market not in [
            "crypto",
            "forex"
        ]:

            await query.answer(
                "❌ بازار انتخاب نشده.",
                show_alert=True
            )

            return


        if not selected:

            await query.answer(
                "❌ حداقل یک کانال یا گروه انتخاب کن.",
                show_alert=True
            )

            return


        context.user_data[
            "report_all_market"
        ] = False


        await query.edit_message_text(

            "📊 کانال‌های انتخاب‌شده ثبت شدند.\n\n"
            "حالا بازه زمانی گزارش را انتخاب کن:",

            reply_markup=(
                report_manager.report_time_keyboard()
            )
        )

        return


    # =====================================================
    # TIME SELECTION
    # =====================================================

    if data.startswith(
        "report_time:"
    ):

        mode = data.split(
            ":",
            1
        )[1]


        market = context.user_data.get(
            "report_market"
        )


        if not market:

            await query.answer(
                "❌ بازار انتخاب نشده.",
                show_alert=True
            )

            return


        # =================================================
        # LOAD LOGS
        # =================================================

        logs = report_manager.load_logs()


        # =================================================
        # MARKET FILTER
        # =================================================

        if market != "all":

            logs = report_manager.filter_by_market(
                logs,
                market
            )


        # =================================================
        # CHANNEL FILTER
        # =================================================

        all_market = context.user_data.get(
            "report_all_market",
            False
        )


        selected = context.user_data.get(
            "report_selected_channels",
            []
        )


        # -------------------------------------------------
        # اگر بازار مشخص است و گزارش همه بازار انتخاب نشده
        # یعنی فقط کانال‌های انتخاب‌شده
        # -------------------------------------------------

        if (
            market != "all"
            and not all_market
        ):

            if not selected:

                await query.answer(
                    "❌ هیچ کانالی انتخاب نشده.",
                    show_alert=True
                )

                return


            logs = report_manager.filter_by_channels(
                logs,
                selected
            )


        # =================================================
        # TIME FILTER
        # =================================================

        if mode == "1m":

            logs = report_manager.filter_by_time(
                logs,
                months=1
            )

        elif mode == "3m":

            logs = report_manager.filter_by_time(
                logs,
                months=3
            )

        elif mode == "6m":

            logs = report_manager.filter_by_time(
                logs,
                months=6
            )

        elif mode == "1y":

            logs = report_manager.filter_by_time(
                logs,
                years=1
            )


        # =================================================
        # EMPTY REPORT
        # =================================================

        if not logs:

            await query.edit_message_text(

                "❌ در این بازه هیچ سیگنالی "
                "برای گزارش پیدا نشد."
            )

            clear_report_state(
                context
            )

            return


        # =================================================
        # FILE NAME
        # =================================================

        if market == "crypto":

            market_name = "crypto"

        elif market == "forex":

            market_name = "forex"

        else:

            market_name = "all"


        filename = (

            report_manager.SIGNAL_LOG_FILE.parent
            / f"report_{market_name}_{mode}.xlsx"
        )


        # =================================================
        # EXPORT
        # =================================================

        filename = await asyncio.to_thread(
            report_manager.export_to_excel,
            logs,
            filename
        )


        # =================================================
        # SEND FILE
        # =================================================

        with open(
            filename,
            "rb"
        ) as f:

            await context.application.bot.send_document(

                chat_id=query.from_user.id,

                document=f,

                caption=(
                    "📊 گزارش آماده شد.\n"
                    f"تعداد سیگنال‌ها: {len(logs)}"
                )
            )


        # =================================================
        # CLEAN STATE
        # =================================================

        clear_report_state(
            context
        )


        await query.edit_message_text(
            "✅ گزارش با موفقیت ارسال شد."
        )

        return
