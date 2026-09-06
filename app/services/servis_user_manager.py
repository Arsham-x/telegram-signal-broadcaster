# -*- coding: utf-8 -*-
import json
import os
from telegram import ReplyKeyboardMarkup
from app.settings.config import (
    USERS_FILE,
    atomic_json_write,
)
# ================== LOAD / SAVE ==================
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return json.loads(content) if content else []
        except (json.JSONDecodeError, OSError):
            return []
    return []

def save_users(users):
    atomic_json_write(USERS_FILE, users)

# ================== ACCESS ==================
def get_user_by_id(users, user_id: int):
    return next((u for u in users if u.get("user_id") == user_id), None)

def is_owner(user_id: int, admin_id: int) -> bool:
    return user_id == admin_id

def is_admin(users, user_id: int, admin_id: int) -> bool:
    if user_id == admin_id:
        return True
    user = get_user_by_id(users, user_id)
    return bool(user and user.get("is_admin"))

# ================== REGISTER ==================
def register_user(users, update):
    user_id = update.effective_user.id
    username = update.effective_user.username or ""

    if any(u.get("user_id") == user_id for u in users):
        return users

    users.append({
        "user_id": user_id,
        "username": username,
        "is_admin": False,
        "is_banned": False
    })
    save_users(users)
    return users

# ================== KEYBOARDS ==================
def user_list_keyboard(users):
    keyboard = []
    for u in users:
        label = u.get("username") or str(u.get("user_id"))
        keyboard.append([label])
    keyboard.append(["🔙 بازگشت"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def user_action_keyboard():
    keyboard = [
        ["⚠️ بن", "✅ آنبن"],
        ["🛡️ مدیر", "❌ لغو مدیر"],
        ["🔙 بازگشت"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)