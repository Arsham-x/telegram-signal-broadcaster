# -*- coding: utf-8 -*-

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from app.services import servis_community_manager as community_manager
from app.services import servis_channel_manager as channel_manager
# ================== CallbackQuery: community ======
async def community_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    # ================= صفحه بندی =================

    if data.startswith("community_channels_page:"):

        page = int(
            data.split(":")[1]
        )


        context.user_data["community_page"] = page


        channels = context.user_data.get(
            "community_channels",
            []
        )

        selected = context.user_data.get(
            "community_selected",
            []
        )


        await query.edit_message_reply_markup(

            reply_markup=
            community_manager.community_channel_keyboard(
                channels,
                selected,
                page
            )
        )

        return
    if data.startswith("community_select:"):

        index = int(
            data.split(":")[1]
        )


        category = context.user_data.get(
            "community_delete_category"
        )


        communities = (
            community_manager
            .get_category_communities(category)
        )


        if index >= len(communities):
            return


        context.user_data["community_delete_index"] = index


        await query.edit_message_text(
            "حذف این کامیونیتی؟",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🗑 حذف کامیونیتی",
                            callback_data="community_delete_confirm"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🔙 بازگشت",
                            callback_data="community_cancel"
                        )
                    ]
                ]
            )
        )

        return
    if data == "community_delete_confirm":

        index = context.user_data.get(
            "community_delete_index"
        )


        if index is None:
            return


        community_manager.remove_community(index)


        await query.edit_message_text(
            "✅ کامیونیتی حذف شد.\nکانال‌ها و گروه‌ها حذف نشدند."
        )


        context.user_data["community_delete_index"] = None

        return
    # ================= انتخاب کانال =================

    if data.startswith("community_toggle:"):

        index = int(data.split(":")[1])


        channels = context.user_data.get(
            "community_channels",
            []
        )


        selected = context.user_data.setdefault(
            "community_selected",
            []
        )


        chat_id = channels[index]["chat_id"]


        if chat_id in selected:
            selected.remove(chat_id)

        else:
            selected.append(chat_id)


        await query.edit_message_reply_markup(

            reply_markup=
            community_manager.community_channel_keyboard(
                channels,
                selected
            )
        )

        return



    # ================= ثبت =================

    if data == "community_save":


        name = context.user_data.get(
            "community_name"
        )

        category = context.user_data.get(
            "community_category"
        )

        selected = context.user_data.get(
            "community_selected",
            []
        )


        if not selected:

            await query.answer(
                "حداقل یک کانال انتخاب کن",
                show_alert=True
            )

            return



        community_manager.add_community(
            name,
            category,
            selected
        )


        await query.edit_message_text(
            "✅ کامیونیتی ساخته شد."
        )


        context.user_data["community_mode"] = None
        context.user_data["community_selected"] = []
        context.user_data["community_page"] = 0


        return



    # ================= لغو =================

    if data == "community_cancel":

        context.user_data["community_mode"] = None
        context.user_data["community_selected"] = []


        await query.edit_message_text(
            "❌ لغو شد."
        )

        return

