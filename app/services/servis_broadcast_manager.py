# -*- coding: utf-8 -*-
from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
)
from telegram.ext import ContextTypes
import asyncio

from app.services.servis_channel_manager import load_channels


BROADCAST_BUTTON_TEXT = "📣 ارسال پیام همگانی"
BROADCAST_CALLBACK = "broadcast_send_all"


# =========================================================
# KEYBOARDS
# =========================================================

def broadcast_keyboard():
    return ReplyKeyboardMarkup(
        [
            [BROADCAST_BUTTON_TEXT],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )


def broadcast_market_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📈 فارکس", "🪙 کریپتو"],
            ["🔀 هر دو"],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )


def broadcast_confirm_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📣 ارسال",
                callback_data=BROADCAST_CALLBACK
            )
        ],
        [
            InlineKeyboardButton(
                "❌ لغو",
                callback_data="broadcast_cancel"
            )
        ]
    ])


# =========================================================
# MARKET FILTER
# =========================================================

def channel_matches_market(channel, market):
    """
    مشخص می‌کند کانال برای بازار انتخاب‌شده مناسب است یا نه.

    crypto:
        crypto + both

    forex:
        forex + both

    both:
        همه کانال‌ها
    """

    if market == "both":
        return True

    category = channel.get("category")

    if category == market:
        return True

    if category == "both":
        return True

    return False


# =========================================================
# START BROADCAST
# =========================================================

async def start_broadcast_flow(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # ابتدا بازار را انتخاب می‌کنیم
    context.user_data["waiting_for_broadcast_market"] = True
    context.user_data["waiting_for_broadcast_message"] = False

    # پاک کردن اطلاعات قبلی
    context.user_data.pop("broadcast_market", None)
    context.user_data.pop("broadcast_message_type", None)
    context.user_data.pop("broadcast_file_id", None)
    context.user_data.pop("broadcast_caption", None)
    context.user_data.pop("broadcast_text", None)

    await update.message.reply_text(
        "📣 پیام برای کدام گروه‌ها و کانال‌ها ارسال شود؟",
        reply_markup=broadcast_market_keyboard()
    )


# =========================================================
# RECEIVE BROADCAST MESSAGE
# =========================================================

async def handle_broadcast_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # =====================================================
    # انتخاب بازار
    # =====================================================

    if context.user_data.get("waiting_for_broadcast_market"):

        market_map = {
            "📈 فارکس": "forex",
            "🪙 کریپتو": "crypto",
            "🔀 هر دو": "both",
        }

        text = (update.message.text or "").strip()

        if text not in market_map:
            return False

        market = market_map[text]

        context.user_data["broadcast_market"] = market
        context.user_data["waiting_for_broadcast_market"] = False
        context.user_data["waiting_for_broadcast_message"] = True

        market_name = {
            "forex": "📈 فارکس",
            "crypto": "🪙 کریپتو",
            "both": "🔀 هر دو",
        }[market]

        await update.message.reply_text(
            f"✅ مقصد انتخاب شد: {market_name}\n\n"
            "حالا پیام موردنظر را بفرست.\n"
            "متن، عکس، ویس، فیلم، GIF یا فایل قابل ارسال است."
        )

        return True

    # =====================================================
    # دریافت پیام
    # =====================================================

    if not context.user_data.get("waiting_for_broadcast_message"):
        return False

    context.user_data["waiting_for_broadcast_message"] = False

    message = update.message

    message_type = None
    file_id = None
    caption = message.caption
    text = message.text

    # ---------------- TEXT ----------------

    if message.text:
        message_type = "text"

    # ---------------- PHOTO ----------------

    elif message.photo:
        message_type = "photo"
        file_id = message.photo[-1].file_id

    # ---------------- VOICE ----------------

    elif message.voice:
        message_type = "voice"
        file_id = message.voice.file_id

    # ---------------- VIDEO ----------------

    elif message.video:
        message_type = "video"
        file_id = message.video.file_id

    # ---------------- GIF / ANIMATION ----------------

    elif message.animation:
        message_type = "animation"
        file_id = message.animation.file_id

    # ---------------- AUDIO ----------------

    elif message.audio:
        message_type = "audio"
        file_id = message.audio.file_id

    # ---------------- DOCUMENT ----------------

    elif message.document:
        message_type = "document"
        file_id = message.document.file_id

    else:
        await update.message.reply_text(
            "❌ این نوع پیام فعلاً پشتیبانی نمی‌شود."
        )

        context.user_data["waiting_for_broadcast_message"] = True

        return True

    # =====================================================
    # ذخیره پیام
    # =====================================================

    context.user_data["broadcast_message_type"] = message_type
    context.user_data["broadcast_file_id"] = file_id
    context.user_data["broadcast_caption"] = caption
    context.user_data["broadcast_text"] = text

    market = context.user_data.get("broadcast_market")

    market_name = {
        "forex": "📈 فارکس",
        "crypto": "🪙 کریپتو",
        "both": "🔀 هر دو",
    }.get(market, "-")

    # =====================================================
    # تعداد مقصدها
    # =====================================================

    channels = load_channels()

    target_channels = [
        ch
        for ch in channels
        if channel_matches_market(ch, market)
    ]

    if not target_channels:

        context.user_data.pop("broadcast_message_type", None)
        context.user_data.pop("broadcast_file_id", None)
        context.user_data.pop("broadcast_caption", None)
        context.user_data.pop("broadcast_text", None)

        await update.message.reply_text(
            f"❌ هیچ کانال یا گروهی برای {market_name} پیدا نشد."
        )

        return True

    # =====================================================
    # تأیید ارسال
    # =====================================================

    await update.message.reply_text(
        "📋 پیام آماده ارسال است.\n\n"
        f"🎯 مقصد: {market_name}\n"
        f"📡 تعداد کانال/گروه: {len(target_channels)}\n"
        f"📦 نوع پیام: {message_type}\n\n"
        "آیا ارسال شود؟",
        reply_markup=broadcast_confirm_keyboard()
    )

    return True


# =========================================================
# SEND MESSAGE TO ONE CHANNEL
# =========================================================

async def send_broadcast_message(
    bot,
    chat_id,
    message_type,
    file_id=None,
    text=None,
    caption=None
):

    if message_type == "text":

        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML"
        )

    elif message_type == "photo":

        await bot.send_photo(
            chat_id=chat_id,
            photo=file_id,
            caption=caption,
            parse_mode="HTML"
        )

    elif message_type == "voice":

        await bot.send_voice(
            chat_id=chat_id,
            voice=file_id,
            caption=caption,
            parse_mode="HTML"
        )

    elif message_type == "video":

        await bot.send_video(
            chat_id=chat_id,
            video=file_id,
            caption=caption,
            parse_mode="HTML"
        )

    elif message_type == "animation":

        await bot.send_animation(
            chat_id=chat_id,
            animation=file_id,
            caption=caption,
            parse_mode="HTML"
        )

    elif message_type == "audio":

        await bot.send_audio(
            chat_id=chat_id,
            audio=file_id,
            caption=caption,
            parse_mode="HTML"
        )

    elif message_type == "document":

        await bot.send_document(
            chat_id=chat_id,
            document=file_id,
            caption=caption,
            parse_mode="HTML"
        )

    else:
        raise ValueError(
            f"Unsupported broadcast message type: {message_type}"
        )


# =========================================================
# CALLBACK
# =========================================================

async def broadcast_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    # =====================================================
    # CANCEL
    # =====================================================

    if query.data == "broadcast_cancel":

        context.user_data.pop(
            "waiting_for_broadcast_market",
            None
        )

        context.user_data.pop(
            "waiting_for_broadcast_message",
            None
        )

        context.user_data.pop(
            "broadcast_market",
            None
        )

        context.user_data.pop(
            "broadcast_message_type",
            None
        )

        context.user_data.pop(
            "broadcast_file_id",
            None
        )

        context.user_data.pop(
            "broadcast_caption",
            None
        )

        context.user_data.pop(
            "broadcast_text",
            None
        )

        await query.edit_message_text(
            "❌ ارسال لغو شد."
        )

        return

    # =====================================================
    # SEND ALL FOR SELECTED MARKET
    # =====================================================

    if query.data != BROADCAST_CALLBACK:
        return

    market = context.user_data.get(
        "broadcast_market"
    )

    message_type = context.user_data.get(
        "broadcast_message_type"
    )

    file_id = context.user_data.get(
        "broadcast_file_id"
    )

    caption = context.user_data.get(
        "broadcast_caption"
    )

    text = context.user_data.get(
        "broadcast_text"
    )

    # =====================================================
    # VALIDATION
    # =====================================================

    if not market:

        await query.answer(
            "بازار انتخاب نشده.",
            show_alert=True
        )

        return

    if not message_type:

        await query.answer(
            "پیامی برای ارسال وجود ندارد.",
            show_alert=True
        )

        return

    # =====================================================
    # REMOVE BUTTONS
    # =====================================================

    await query.edit_message_reply_markup(
        reply_markup=None
    )

    # =====================================================
    # GET TARGET CHANNELS
    # =====================================================

    channels = load_channels()

    target_channels = [
        ch
        for ch in channels
        if channel_matches_market(ch, market)
    ]

    # =====================================================
    # SEND
    # =====================================================

    sent = 0
    failed = 0

    for ch in target_channels:

        chat_id = ch["chat_id"]

        try:

            await send_broadcast_message(
                bot=context.application.bot,
                chat_id=chat_id,
                message_type=message_type,
                file_id=file_id,
                text=text,
                caption=caption
            )

            sent += 1

            await asyncio.sleep(0.1)

        except Exception as e:

            failed += 1

            print(
                f"FAILED BROADCAST | "
                f"CHANNEL: {chat_id} | "
                f"TYPE: {message_type} | "
                f"ERROR: {e}"
            )

    # =====================================================
    # CLEAN STATE
    # =====================================================

    context.user_data.pop(
        "waiting_for_broadcast_market",
        None
    )

    context.user_data.pop(
        "waiting_for_broadcast_message",
        None
    )

    context.user_data.pop(
        "broadcast_market",
        None
    )

    context.user_data.pop(
        "broadcast_message_type",
        None
    )

    context.user_data.pop(
        "broadcast_file_id",
        None
    )

    context.user_data.pop(
        "broadcast_caption",
        None
    )

    context.user_data.pop(
        "broadcast_text",
        None
    )

    market_name = {
        "forex": "📈 فارکس",
        "crypto": "🪙 کریپتو",
        "both": "🔀 هر دو",
    }.get(market, "-")

    # =====================================================
    # RESULT
    # =====================================================

    await query.message.reply_text(
        f"✅ ارسال همگانی انجام شد.\n\n"
        f"🎯 مقصد: {market_name}\n"
        f"📦 نوع پیام: {message_type}\n"
        f"📡 تعداد مقصد: {len(target_channels)}\n\n"
        f"موفق: {sent}\n"
        f"ناموفق: {failed}"
    )