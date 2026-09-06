# -*- coding: utf-8 -*-
from telegram import (
    Update,
    ReplyKeyboardMarkup,
)

from telegram.ext import ContextTypes

from app.services import (
    servis_channel_manager as channel_manager
)

from app.services import (
    servis_community_manager as community_manager
)


async def handle_community_manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = (update.message.text or "").strip()

    # =====================================================
    # مدیریت کامیونیتی
    # =====================================================

    if text == "👥 مدیریت کامیونیتی":

        await update.message.reply_text(
            "مدیریت کامیونیتی:",
            reply_markup=community_manager.community_manage_keyboard()
        )

        return True

    # =====================================================
    # ایجاد کامیونیتی
    # =====================================================

    if text == "➕ ایجاد کامیونیتی":
        context.user_data["waiting_for_channel_add"] = False
        context.user_data["waiting_for_channel_category"] = False
        context.user_data["new_channel"] = None
        context.user_data["community_mode"] = "create"
        context.user_data["community_category"] = None
        context.user_data["community_name"] = None
        context.user_data["waiting_community_name"] = False
        context.user_data["community_channels"] = None
        context.user_data["community_selected"] = []
        context.user_data["community_page"] = 0
        await update.message.reply_text(
            "کامیونیتی برای کدام بازار است؟",
            reply_markup=community_manager.category_keyboard()
        )
        return True
    # =====================================================
    # حذف کامیونیتی
    # =====================================================

    if text == "🗑 حذف کامیونیتی":
        context.user_data["waiting_for_channel_add"] = False
        context.user_data["waiting_for_channel_category"] = False
        context.user_data["new_channel"] = None
        context.user_data["community_mode"] = "delete"
        context.user_data["community_category"] = None
        context.user_data["community_name"] = None
        context.user_data["waiting_community_name"] = False
        context.user_data["community_channels"] = None
        context.user_data["community_selected"] = []
        context.user_data["community_page"] = 0
        context.user_data["waiting_delete_community"] = False
        context.user_data["community_delete_category"] = None
        context.user_data["delete_community_index"] = None
        context.user_data["delete_inside_mode"] = False
        context.user_data["delete_inside_selected"] = []
        await update.message.reply_text(
            "کدام بازار؟",
            reply_markup=community_manager.category_keyboard()
        )

        return True

    # =====================================================
    # انتخاب بازار برای ساخت کامیونیتی
    # =====================================================

    if context.user_data.get("community_mode") == "create":

        category_map = {
            "🪙 کریپتو": "crypto",
            "📈 فارکس": "forex"
        }

        if text in category_map:

            context.user_data["community_category"] = category_map[text]
            context.user_data["waiting_community_name"] = True

            await update.message.reply_text(
                "نام کامیونیتی را وارد کن:"
            )

            return True

    # =====================================================
    # انتخاب بازار برای حذف کامیونیتی
    # =====================================================

    if context.user_data.get("community_mode") == "delete":

        category_map = {
            "🪙 کریپتو": "crypto",
            "📈 فارکس": "forex"
        }

        if text in category_map:

            category = category_map[text]

            context.user_data["community_delete_category"] = category
            context.user_data["waiting_delete_community"] = True

            communities = (
                community_manager.get_category_communities(
                    category
                )
            )

            if not communities:

                await update.message.reply_text(
                    "کامیونیتی‌ای وجود ندارد."
                )

                return True

            await update.message.reply_text(
                "کامیونیتی موردنظر را انتخاب کن:",
                reply_markup=community_manager.community_list_keyboard(
                    communities
                )
            )

            return True

        # =================================================
        # انتخاب کامیونیتی
        # =================================================

        if context.user_data.get("waiting_delete_community"):

            communities = (
                community_manager.get_category_communities(
                    context.user_data.get(
                        "community_delete_category"
                    )
                )
            )

            for c in communities:

                if text == c["name"]:

                    context.user_data[
                        "delete_community_index"
                    ] = c["index"]

                    context.user_data[
                        "waiting_delete_community"
                    ] = False

                    await update.message.reply_text(
                        "چه چیزی حذف شود?",
                        reply_markup=ReplyKeyboardMarkup(
                            [
                                ["🗑 حذف کل کامیونیتی"],
                                ["📋 حذف از داخل کامیونیتی"],
                                ["🔙 بازگشت"]
                            ],
                            resize_keyboard=True
                        )
                    )

                    return True

        # =================================================
        # حذف کل کامیونیتی
        # =================================================

        if text == "🗑 حذف کل کامیونیتی":

            index = context.user_data.get(
                "delete_community_index"
            )

            if index is not None:

                community_manager.delete_community(
                    index
                )

                context.user_data[
                    "delete_community_index"
                ] = None

                context.user_data[
                    "community_delete_category"
                ] = None

                await update.message.reply_text(
                    "✅ کامیونیتی کامل حذف شد.",
                    reply_markup=community_manager.community_manage_keyboard()
                )

            return True

        # =================================================
        # حذف از داخل کامیونیتی
        # =================================================

        if text == "📋 حذف از داخل کامیونیتی":

            index = context.user_data.get(
                "delete_community_index"
            )

            if index is None:
                return True

            community = (
                community_manager.get_community_by_index(
                    index
                )
            )

            if not community:

                await update.message.reply_text(
                    "کامیونیتی پیدا نشد."
                )

                return True

            context.user_data["delete_inside_mode"] = True
            context.user_data["delete_inside_selected"] = []
            context.user_data["delete_inside_page"] = 0

            await update.message.reply_text(
                "مواردی که می‌خواهی حذف شوند را انتخاب کن:",
                reply_markup=community_manager.community_delete_channel_keyboard(
                    community["channels"],
                    [],
                    0
                )
            )

            return True

        # =================================================
        # حذف موارد انتخاب شده
        # =================================================

        if text == "🗑 حذف انتخاب‌شده‌ها":

            index = context.user_data.get(
                "delete_community_index"
            )

            selected = context.user_data.get(
                "delete_inside_selected",
                []
            )

            if not selected:

                await update.message.reply_text(
                    "❌ چیزی انتخاب نشده."
                )

                return True

            community_manager.delete_community_channels(
                index,
                selected
            )

            context.user_data["delete_inside_mode"] = False
            context.user_data["delete_inside_selected"] = []

            await update.message.reply_text(
                "✅ موارد انتخاب شده حذف شدند.",
                reply_markup=community_manager.community_manage_keyboard()
            )

            return True

        # =================================================
        # انصراف از حذف داخلی
        # =================================================

        if text == "❌ انصراف و بازگشت":

            context.user_data["delete_inside_mode"] = False
            context.user_data["delete_inside_selected"] = []

            await update.message.reply_text(
                "لغو شد.",
                reply_markup=community_manager.community_manage_keyboard()
            )

            return True

        # =================================================
        # انتخاب کانال برای حذف
        # =================================================

        if context.user_data.get("delete_inside_mode"):

            selected = context.user_data.get(
                "delete_inside_selected",
                []
            )

            community = (
                community_manager.get_community_by_index(
                    context.user_data[
                        "delete_community_index"
                    ]
                )
            )

            if not community:
                return True

            channels = community["channels"]

            if text.startswith("✅ "):

                name = text.replace("✅ ", "")

                for ch in channels:

                    cid = (
                        ch
                        if isinstance(ch, int)
                        else ch["chat_id"]
                    )

                    if (
                        community_manager.get_channel_title(cid)
                        == name
                    ):

                        if cid in selected:
                            selected.remove(cid)
                        else:
                            selected.append(cid)

                        break

            else:

                for ch in channels:

                    cid = (
                        ch
                        if isinstance(ch, int)
                        else ch["chat_id"]
                    )

                    if (
                        community_manager.get_channel_title(cid)
                        == text
                    ):

                        if cid not in selected:
                            selected.append(cid)

                        break

            context.user_data[
                "delete_inside_selected"
            ] = selected

            await update.message.reply_text(
                "مواردی که می‌خواهی حذف شوند:",
                reply_markup=community_manager.community_delete_channel_keyboard(
                    channels,
                    selected,
                    0
                )
            )

            return True

    # =====================================================
    # دریافت نام کامیونیتی
    # =====================================================
    
    if context.user_data.get("waiting_community_name"):
    
        context.user_data["community_name"] = text
        context.user_data["waiting_community_name"] = False
    
        category = context.user_data.get(
            "community_category"
        )
    
        channels = channel_manager.load_channels()
        communities = community_manager.load_communities()
    
        # =====================================================
        # کانال‌هایی که قبلاً در همین بازار استفاده شده‌اند
        # =====================================================
    
        used_channels = set()
    
        for community in communities:
    
            # فقط کامیونیتی‌های همین بازار
            if community.get("category") != category:
                continue
    
            for channel in community.get(
                "channels",
                []
            ):
    
                if isinstance(channel, dict):
                    chat_id = channel.get("chat_id")
                else:
                    chat_id = channel
    
                if chat_id is not None:
                    used_channels.add(chat_id)
    
        # =====================================================
        # فیلتر کانال‌ها
        # =====================================================
    
        filtered = []
    
        for channel in channels:
    
            channel_category = channel.get(
                "category"
            )
    
            chat_id = channel.get(
                "chat_id"
            )
    
            # کانال باید برای این بازار مناسب باشد
            category_ok = (
                channel_category == category
                or channel_category == "both"
                or channel_category is None
            )
    
            # کانال نباید قبلاً در کامیونیتی همین بازار استفاده شده باشد
            not_used = (
                chat_id not in used_channels
            )
    
            if category_ok and not_used:
                filtered.append(channel)
    
        # =====================================================
        # ذخیره لیست برای ادامه مراحل
        # =====================================================
    
        context.user_data[
            "community_channels"
        ] = filtered
    
        context.user_data[
            "community_selected"
        ] = []
    
        context.user_data[
            "community_page"
        ] = 0
    
        # =====================================================
        # اگر چیزی پیدا نشد
        # =====================================================
    
        if not filtered:
    
            context.user_data[
                "community_channels"
            ] = None
    
            context.user_data[
                "community_selected"
            ] = []
    
            context.user_data[
                "waiting_community_name"
            ] = False
    
            await update.message.reply_text(
                "❌ هیچ کانال یا گروه مناسبی برای این بازار پیدا نشد.\n\n"
                f"تعداد کل کانال‌ها و گروه‌های ثبت‌شده: {len(channels)}\n"
                f"بازار انتخاب‌شده: {category}"
            )
    
            return True
    
        # =====================================================
        # نمایش کانال‌ها
        # =====================================================
    
        await update.message.reply_text(
            f"✅ {len(filtered)} کانال/گروه برای انتخاب پیدا شد.\n"
            "کانال‌ها و گروه‌ها را انتخاب کن:",
            reply_markup=community_manager.community_channel_keyboard(
                filtered,
                [],
                0,
                "create"
            )
        )
    
        return True
    # =====================================================
    # عملیات انتخاب کانال‌های کامیونیتی
    # =====================================================

    if context.user_data.get("community_channels"):

        channels = context.user_data[
            "community_channels"
        ]

        selected = context.user_data[
            "community_selected"
        ]

        page = context.user_data.get(
            "community_page",
            0
        )

        # صفحه بعد

        if text == "➡️ بعدی":

            page += 1

            context.user_data[
                "community_page"
            ] = page

            await update.message.reply_text(
                "صفحه بعد:",
                reply_markup=community_manager.community_channel_keyboard(
                    channels,
                    selected,
                    page
                )
            )

            return True

        # صفحه قبل

        if text == "⬅️ قبلی":

            page = max(
                0,
                page - 1
            )

            context.user_data[
                "community_page"
            ] = page

            await update.message.reply_text(
                "صفحه قبل:",
                reply_markup=community_manager.community_channel_keyboard(
                    channels,
                    selected,
                    page
                )
            )

            return True

        # ثبت کامیونیتی

        if text == "✅ ثبت لیست":

            if not selected:

                await update.message.reply_text(
                    "حداقل یک کانال یا گروه انتخاب کن."
                )

                return True

            community_manager.save_community(
                name=context.user_data[
                    "community_name"
                ],
                category=context.user_data[
                    "community_category"
                ],
                channels=selected
            )

            context.user_data.pop(
                "community_channels",
                None
            )

            context.user_data.pop(
                "community_selected",
                None
            )

            context.user_data.pop(
                "community_name",
                None
            )

            await update.message.reply_text(
                "✅ کامیونیتی ساخته شد.",
                reply_markup=community_manager.community_manage_keyboard()
            )

            return True

        # لغو

        if text == "❌ انصراف و بازگشت":

            context.user_data.pop(
                "community_channels",
                None
            )

            context.user_data.pop(
                "community_selected",
                None
            )

            context.user_data.pop(
                "community_name",
                None
            )

            await update.message.reply_text(
                "لغو شد.",
                reply_markup=community_manager.community_manage_keyboard()
            )

            return True

        # انتخاب کانال

        clean_text = text.replace(
            "✅ ",
            ""
        )

        for ch in channels:

            title = (
                ch.get("title")
                or str(ch["chat_id"])
            )

            if clean_text == title:

                cid = ch["chat_id"]

                if cid in selected:
                    selected.remove(cid)
                else:
                    selected.append(cid)

                await update.message.reply_text(
                    "انتخاب شد:",
                    reply_markup=community_manager.community_channel_keyboard(
                        channels,
                        selected,
                        context.user_data.get(
                            "community_page",
                            0
                        )
                    )
                )

                return True

    # =====================================================
    # چیزی مربوط به کامیونیتی نبود
    # =====================================================

    return False
