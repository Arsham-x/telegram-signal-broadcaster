# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from app.services import servis_signal_manager as signal_manager


async def signal_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    data = context.user_data.get(
        "signal",
        {}
    ).get(user_id)

    if not data:

        await query.answer(
            "سیگنالی فعال نیست.",
            show_alert=True
        )

        return

    data.setdefault(
        "selected_communities",
        []
    )

    # =====================================================
    # لغو پیش‌نمایش
    # =====================================================

    if query.data == "signal_preview_cancel":

        context.user_data[
            "signal"
        ].pop(user_id, None)

        context.user_data[
            "waiting_for_signal_flow"
        ] = False

        await query.edit_message_text(
            "❌ ارسال سیگنال لغو شد."
        )

        return


    # =====================================================
    # ادامه پیش‌نمایش → کامیونیتی‌ها
    # =====================================================

    if query.data == "signal_preview_continue":

        await query.edit_message_reply_markup(
            reply_markup=None
        )

        market = data.get("market")

        communities = (
            signal_manager.get_market_communities(
                market
            )
        )

        if not communities:

            await query.message.reply_text(
                f"❌ برای بازار {market} "
                "هیچ کامیونیتی‌ای ثبت نشده."
            )

            return

        data["step"] = "communities"

        await query.message.reply_text(
            "📣 کامیونیتی‌های مربوط به "
            f"{market} را انتخاب کن:",
            reply_markup=(
                signal_manager.communities_inline_keyboard(
                    market,
                    data["selected_communities"]
                )
            )
        )

        return


    # =====================================================
    # انتخاب / عدم انتخاب کامیونیتی
    # =====================================================
    
    if query.data.startswith("toggle_community:"):
    
        community_name = query.data[
            len("toggle_community:"):
        ]
    
        selected = data.setdefault(
            "selected_communities",
            []
        )
    
        if community_name in selected:
            selected.remove(community_name)
        else:
            selected.append(community_name)
    
        print(
            "[SIGNAL COMMUNITY TOGGLE]",
            "market =", data.get("market"),
            "community =", community_name,
            "selected =", selected
        )
    
        await query.edit_message_reply_markup(
            reply_markup=(
                signal_manager.communities_inline_keyboard(
                    data["market"],
                    selected
                )
            )
        )
    
        return
    # =====================================================
    # جلوگیری از ارسال دوباره
    # =====================================================

    if context.user_data.get(
        "sending_signal"
    ):

        return


    # =====================================================
    # ارسال به کامیونیتی‌های انتخاب‌شده
    # =====================================================

    if query.data == "send_signal_communities":

        selected_names = data.get(
            "selected_communities",
            []
        )
    
        if not selected_names:
    
            await query.answer(
                "حداقل یک کامیونیتی انتخاب کن ❗",
                show_alert=True
            )
    
            return
    
        chat_ids = (
            signal_manager
            .get_channels_from_communities(
                data["market"],
                selected_names=selected_names
            )
        )
    
        if not chat_ids:
    
            await query.answer(
                "برای کامیونیتی‌های انتخاب‌شده هیچ مقصدی پیدا نشد.",
                show_alert=True
            )
    
            return
    
        print(
            "[SIGNAL SEND SELECTED]",
            "market =", data["market"],
            "communities =", selected_names,
            "chat_ids =", chat_ids
        )
    
        await _send_signal(
            update,
            context,
            data,
            chat_ids,
            selected_names,
            send_mode="selected"
        )
    
        return


    # =====================================================
    # ارسال به تمام کامیونیتی‌های Market
    # =====================================================

    if query.data == "send_signal_all_communities":

        all_communities = (
            signal_manager.get_market_communities(
                data["market"]
            )
        )
    
        if not all_communities:
    
            await query.answer(
                "برای این بازار هیچ کامیونیتی‌ای ثبت نشده.",
                show_alert=True
            )
    
            return
    
        chat_ids = (
            signal_manager
            .get_channels_from_communities(
                data["market"],
                all_communities=True
            )
        )
    
        if not chat_ids:
    
            await query.answer(
                "برای این بازار هیچ مقصدی پیدا نشد.",
                show_alert=True
            )
    
            return
    
        all_names = [
            community["name"]
            for community in all_communities
        ]
    
        data["selected_communities"] = all_names
    
        print(
            "[SIGNAL SEND ALL]",
            "market =", data["market"],
            "communities =", all_names,
            "chat_ids =", chat_ids
        )
    
        await _send_signal(
            update,
            context,
            data,
            chat_ids,
            all_names,
            send_mode="all"
        )
    
        return
# =========================================================
# ارسال واقعی
# =========================================================

async def _send_signal(
    update,
    context,
    data,
    chat_ids,
    community_names,
    send_mode
):

    query = update.callback_query
    print(
    "[SIGNAL CALLBACK RECEIVED]",
    "data =", query.data,
    "user_id =", query.from_user.id
    )
    
    await query.answer()
    user_id = query.from_user.id

    context.user_data[
        "sending_signal"
    ] = True

    try:

        await query.edit_message_reply_markup(
            reply_markup=None
        )

        message = (
            signal_manager
            .build_signal_message_premium(data)
        )

        # =====================================================
        # چک سلامت کانال‌ها قبل از ارسال
        # =====================================================

        healthy_ids, failed_ids = (
            await signal_manager.check_channels_health(
                context.application.bot,
                chat_ids
            )
        )

        if failed_ids:
            await query.message.reply_text(
                f"⚠️ {len(failed_ids)} کانال غیرقابل دسترس:\n"
                + "\n".join(
                    str(cid) for cid in failed_ids
                )
                + "\n\nبه بقیه ارسال میشه..."
            )

        if not healthy_ids:
            await query.message.reply_text(
                "❌ هیچ کانالی در دسترس نیست!"
            )
            return

        sent_to = []
        message_map = {}

        tasks = [
            context.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="HTML"
            )
            for chat_id in healthy_ids
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

        for chat_id, result in zip(
            healthy_ids,
            results
        ):
        
            if not isinstance(
                result,
                Exception
            ):
        
                message_map[
                    str(chat_id)
                ] = result.message_id
        
                sent_to.append(
                    chat_id
                )
        
            else:
        
                print(
                    f"[SIGNAL SEND ERROR] "
                    f"{chat_id}: {result}"
                )
        
        
        if not sent_to:
        
            await query.answer(
                "❌ ارسال سیگنال به هیچ‌کدام از مقصدها موفق نبود.",
                show_alert=True
            )
        
            return


        # =================================================
        # لاگ جدید
        # =================================================

        log_data = {

            "market": data.get(
                "market"
            ),

            "symbol": data.get(
                "symbol"
            ),

            "position": data.get(
                "position"
            ),

            "leverage": data.get(
                "leverage"
            ),

            "order_type": data.get(
                "order_type"
            ),

            "entries": data.get(
                "entries",
                []
            ),

            "sl": data.get(
                "sl"
            ),

            "tps": data.get(
                "tps",
                []
            ),

            "communities": community_names,

            "message_ids": message_map,

            "channels": sent_to,

            "date": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "status": "active"
        }

        await signal_manager.save_signal_log(
            log_data
        )


        # =================================================
        # پایان session
        # =================================================

        context.user_data[
            "signal"
        ].pop(user_id, None)

        context.user_data[
            "waiting_for_signal_flow"
        ] = False


        if send_mode == "all":

            text = (
                "📣 سیگنال به تمام "
                "کامیونیتی‌های "
                f"{data.get('market')} "
                "ارسال شد.\n\n"
                f"📊 تعداد مقصدهای موفق: "
                f"{len(sent_to)}"
            )

        else:

            text = (
                "✅ سیگنال ارسال شد.\n\n"
                f"👥 کامیونیتی‌ها: "
                f"{len(community_names)}\n"
                f"📊 مقصدهای موفق: "
                f"{len(sent_to)}"
            )


        await query.message.reply_text(
            text
        )

    finally:

        context.user_data[
            "sending_signal"
        ] = False        