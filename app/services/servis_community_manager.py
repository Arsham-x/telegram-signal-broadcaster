# -*- coding: utf-8 -*-
import json
import os

from telegram import ReplyKeyboardMarkup

from app.settings.config import (
    COMMUNITIES_FILE,
    CHANNELS_FILE,
    atomic_json_write,
)

ITEMS_PER_PAGE = 10


# =========================================================
# LOAD / SAVE COMMUNITIES
# =========================================================

def load_communities():
    if not os.path.exists(COMMUNITIES_FILE):
        return []

    try:
        with open(
            COMMUNITIES_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            content = f.read().strip()

        if not content:
            return []

        data = json.loads(content)

        if isinstance(data, list):
            return data

    except Exception as e:
        print("load_communities error:", e)

    return []


def save_communities(data):
    atomic_json_write(COMMUNITIES_FILE, data)

    # invalidate communities cache in signal_manager
    from app.services import servis_signal_manager as _sm
    _sm._invalidate_communities_cache()


# =========================================================
# COMMUNITY MAIN KEYBOARD
# =========================================================

def community_manage_keyboard():

    return ReplyKeyboardMarkup(
        [
            ["➕ ایجاد کامیونیتی"],
            ["🗑 حذف کامیونیتی"],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )


# =========================================================
# CATEGORY KEYBOARD
# =========================================================

def category_keyboard():

    return ReplyKeyboardMarkup(
        [
            ["🪙 کریپتو", "📈 فارکس"],
            ["🔙 بازگشت"]
        ],
        resize_keyboard=True
    )


# =========================================================
# COMMUNITY LIST KEYBOARD
# =========================================================

def community_list_keyboard(communities, page=0):

    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    keyboard = []

    for item in communities[start:end]:

        keyboard.append(
            [
                item["name"]
            ]
        )

    navigation = []

    if page > 0:
        navigation.append("⬅️ قبلی")

    if end < len(communities):
        navigation.append("➡️ بعدی")

    if navigation:
        keyboard.append(navigation)

    keyboard.append(
        ["🔙 بازگشت"]
    )

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# =========================================================
# ADD COMMUNITY
# =========================================================

def add_community(name, category, channels):

    data = load_communities()

    data.append(
        {
            "name": name,
            "category": category,
            "channels": channels
        }
    )

    save_communities(data)


def save_community(name, category, channels):

    add_community(
        name,
        category,
        channels
    )


# =========================================================
# DELETE COMMUNITY
# =========================================================

def delete_community(index):

    data = load_communities()

    if 0 <= index < len(data):
        data.pop(index)

    save_communities(data)


def remove_community(index):

    delete_community(index)


# =========================================================
# GET COMMUNITIES BY CATEGORY
# =========================================================

def get_category_communities(category):

    data = load_communities()

    result = []

    for index, community in enumerate(data):

        if community.get("category") == category:

            result.append(
                {
                    "index": index,
                    "name": community.get(
                        "name",
                        "بدون نام"
                    )
                }
            )

    return result


# =========================================================
# GET COMMUNITY
# =========================================================

def get_community_by_index(index):

    data = load_communities()

    if index < 0 or index >= len(data):
        return None

    return data[index]


# =========================================================
# GET CHANNEL TITLE
# =========================================================

def get_channel_title(chat_id):

    if not os.path.exists(CHANNELS_FILE):
        return str(chat_id)

    try:

        with open(
            CHANNELS_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            channels = json.load(f)

        for channel in channels:

            if channel.get("chat_id") == chat_id:

                return (
                    channel.get("title")
                    or str(chat_id)
                )

    except Exception as e:

        print("get_channel_title error:", e)

    return str(chat_id)


# =========================================================
# CHANNEL SELECT KEYBOARD
# =========================================================

def community_channel_keyboard(
    channels,
    selected,
    page=0,
    mode="create"
):

    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    keyboard = []

    for channel in channels[start:end]:

        chat_id = channel["chat_id"]

        title = (
            channel.get("title")
            or str(chat_id)
        )

        if chat_id in selected:
            label = f"✅ {title}"
        else:
            label = title

        keyboard.append(
            [label]
        )

    navigation = []

    if page > 0:
        navigation.append("⬅️ قبلی")

    if end < len(channels):
        navigation.append("➡️ بعدی")

    if navigation:
        keyboard.append(navigation)

    if mode == "create":

        keyboard.append(
            ["✅ ثبت لیست"]
        )

    elif mode == "delete":

        keyboard.append(
            ["🗑 حذف انتخاب‌شده‌ها"]
        )

    keyboard.append(
        ["❌ انصراف و بازگشت"]
    )

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# =========================================================
# COMMUNITY DELETE CHANNEL KEYBOARD
# =========================================================

def community_delete_channel_keyboard(
    channels,
    selected,
    page=0
):

    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    keyboard = []

    for channel in channels[start:end]:

        if isinstance(channel, dict):

            chat_id = channel["chat_id"]

            title = (
                channel.get("title")
                or str(chat_id)
            )

        else:

            chat_id = channel

            title = get_channel_title(
                chat_id
            )

        if chat_id in selected:
            label = f"✅ {title}"
        else:
            label = title

        keyboard.append(
            [label]
        )

    navigation = []

    if page > 0:
        navigation.append("⬅️ قبلی")

    if end < len(channels):
        navigation.append("➡️ بعدی")

    if navigation:
        keyboard.append(navigation)

    keyboard.append(
        ["🗑 حذف انتخاب‌شده‌ها"]
    )

    keyboard.append(
        ["❌ انصراف و بازگشت"]
    )

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# =========================================================
# DELETE CHANNELS FROM COMMUNITY
# =========================================================

def delete_community_channels(
    index,
    remove_ids
):

    communities = load_communities()

    if index < 0 or index >= len(communities):
        return

    current_channels = communities[index].get(
        "channels",
        []
    )

    new_channels = []

    for channel in current_channels:

        if isinstance(channel, dict):

            chat_id = channel.get(
                "chat_id"
            )

        else:

            chat_id = channel

        if chat_id not in remove_ids:

            new_channels.append(
                channel
            )

    communities[index]["channels"] = new_channels

    save_communities(
        communities
    )