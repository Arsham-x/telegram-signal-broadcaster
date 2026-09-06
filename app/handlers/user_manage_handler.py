from telegram import Update
from telegram.ext import ContextTypes

from app.settings.config import ADMIN_ID

from app.services.servis_user_manager import (
    get_user_by_id,
    is_owner,
    save_users,
    user_list_keyboard,
    user_action_keyboard,
)


async def handle_user_manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    users = context.application.bot_data.get(
        "users",
        []
    )

    user_id = update.effective_user.id
    text = (update.message.text or "").strip()

    # ================== مدیریت کاربران ==================

    if text == "👥 مدیریت کاربران":

        if not is_owner(user_id, ADMIN_ID):
            await update.message.reply_text(
                "فقط ادمین اصلی اجازه این بخش را دارد."
            )
            return True

        await update.message.reply_text(
            "یک کاربر انتخاب کنید:",
            reply_markup=user_list_keyboard(users)
        )

        return True

    # ================== انتخاب کاربر ==================

    for u in users:

        label = (
            u.get("username")
            or str(u.get("user_id"))
        )

        if text == label:

            if not is_owner(user_id, ADMIN_ID):
                await update.message.reply_text(
                    "فقط ادمین اصلی می‌تواند مدیریت کند."
                )
                return True

            context.user_data["selected_user_id"] = u["user_id"]
            context.user_data["waiting_for_user_action"] = True

            status = (
                "❌ بن شده"
                if u.get("is_banned")
                else "✅ فعال"
            )

            role = (
                "👑 Owner"
                if u["user_id"] == ADMIN_ID
                else (
                    "🛡️ مدیر"
                    if u.get("is_admin")
                    else "کاربر عادی"
                )
            )

            await update.message.reply_text(
                f"کاربر انتخاب شد:\n"
                f"وضعیت: {status}\n"
                f"نقش: {role}",
                reply_markup=user_action_keyboard()
            )

            return True

    # ================== عملیات روی کاربر ==================

    if (
        context.user_data.get("waiting_for_user_action")
        and context.user_data.get("selected_user_id")
    ):

        target = get_user_by_id(
            users,
            context.user_data["selected_user_id"]
        )

        if not target:
            await update.message.reply_text(
                "کاربر یافت نشد."
            )
            return True

        if target["user_id"] == ADMIN_ID:

            await update.message.reply_text(
                "امکان تغییر روی Owner وجود ندارد."
            )

            context.user_data[
                "waiting_for_user_action"
            ] = False

            context.user_data[
                "selected_user_id"
            ] = None

            return True

        if target["user_id"] == user_id:

            await update.message.reply_text(
                "نمی‌توانید روی خودتان عملیات انجام دهید."
            )

            return True

        if text == "⚠️ بن":
            target["is_banned"] = True

        elif text == "✅ آنبن":
            target["is_banned"] = False

        elif text == "🛡️ مدیر":
            target["is_admin"] = True

        elif text == "❌ لغو مدیر":
            target["is_admin"] = False

        else:
            await update.message.reply_text(
                "یکی از عملیات‌ها را انتخاب کن."
            )
            return True

        save_users(users)

        context.application.bot_data["users"] = users

        context.user_data[
            "waiting_for_user_action"
        ] = False

        context.user_data[
            "selected_user_id"
        ] = None

        await update.message.reply_text(
            "✅ عملیات انجام شد.",
            reply_markup=user_list_keyboard(users)
        )

        return True

    return False