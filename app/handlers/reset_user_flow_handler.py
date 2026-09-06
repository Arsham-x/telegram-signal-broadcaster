# -*- coding: utf-8 -*-

from app.services import servis_signal_manager as signal_manager


def reset_user_flow(context):
    """
    Reset تمام stateهای موقت کاربر.
    این تابع هنگام 🔙 بازگشت یا شروع یک Flow جدید استفاده می‌شود.
    """

    user_data = context.user_data

    # =========================
    # SYMBOL
    # =========================

    user_data.pop("waiting_for_symbol", None)
    user_data.pop("waiting_for_signal_symbol", None)
    user_data.pop("symbol_page", None)
    user_data.pop("symbol_category", None)
    user_data.pop("symbol_action", None)
    user_data.pop("symbol_flow", None)

    # =========================
    # SIGNAL NEW
    # =========================

    user_data.pop("waiting_for_signal_market", None)
    user_data.pop("waiting_for_signal_symbol", None)
    user_data.pop("waiting_for_signal_flow", None)

    # پاک کردن signal state از dict سراسری ماژول
    # بدون این کار، هر سیگنال نیمه‌کاره‌ای
    # برای همیشه در حافظه می‌ماند (memory leak)
    old_signal = user_data.pop("signal", None)
    if old_signal:
        for uid in list(old_signal.keys()):
            signal_manager.signal_state.pop(uid, None)

    user_data.pop("signal_market", None)
    user_data.pop("signal_symbols", None)

    # =========================
    # SIGNAL MANAGEMENT
    # =========================

    user_data.pop("signal_management_mode", None)
    user_data.pop("signal_management_market", None)
    user_data.pop("waiting_for_signal_hide_id", None)

    # =========================
    # USER MANAGEMENT
    # =========================

    user_data.pop("waiting_for_user_action", None)
    user_data.pop("selected_user_id", None)

    # =========================
    # CHANNEL
    # =========================

    user_data.pop("waiting_for_channel_add", None)
    user_data.pop("waiting_for_channel_category", None)
    user_data.pop("new_channel", None)

    # =========================
    # COMMUNITY
    # =========================

    user_data.pop("community_mode", None)
    user_data.pop("community_category", None)
    user_data.pop("community_name", None)
    user_data.pop("waiting_community_name", None)

    user_data.pop("community_channels", None)
    user_data.pop("community_selected", None)
    user_data.pop("community_page", None)

    user_data.pop("waiting_delete_community", None)
    user_data.pop("community_delete_category", None)
    user_data.pop("delete_community_index", None)

    user_data.pop("community_delete_channels", None)
    user_data.pop("community_delete_selected", None)
    user_data.pop("community_delete_index", None)

    user_data.pop("delete_inside_mode", None)
    user_data.pop("delete_inside_selected", None)
    user_data.pop("delete_inside_page", None)

    # =========================
    # REPORT
    # =========================

    user_data.pop("waiting_for_report_channel", None)
    user_data.pop("report_market", None)
    user_data.pop("report_selected_channels", None)
    user_data.pop("report_all_market", None)

    # =========================
    # REPLY
    # =========================

    user_data.pop("reply_flow", None)
    user_data.pop("reply_market", None)
    user_data.pop("reply_mode", None)
    user_data.pop("reply_manual_mode", None)
    user_data.pop("waiting_manual_reply", None)
    user_data.pop("selected_reply_signal", None)

    # =========================
    # REPLY TEXT
    # =========================

    user_data.pop("waiting_for_reply_text", None)

    # =========================
    # BROADCAST
    # =========================

    user_data.pop("waiting_for_broadcast_market", None)
    user_data.pop("waiting_for_broadcast_message", None)
    user_data.pop("broadcast_market", None)
    user_data.pop("broadcast_message_type", None)
    user_data.pop("broadcast_file_id", None)
    user_data.pop("broadcast_caption", None)
    user_data.pop("broadcast_text", None)