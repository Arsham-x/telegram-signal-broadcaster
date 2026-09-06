# -*- coding: utf-8 -*-

from telegram.ext import CallbackQueryHandler

from app.callbacks.channel_callback import channel_callback
from app.callbacks.community_callback import community_callback
from app.callbacks.signal_callback import signal_callback
from app.callbacks.callback_report import report_callback
from app.callbacks.signal_callback_manage import signal_manage_callback
from app.callbacks.reply_callback import reply_callback
from app.services.servis_broadcast_manager import broadcast_callback

def register_callbacks(application):

    # =====================================================
    # CHANNEL
    # =====================================================

    application.add_handler(
        CallbackQueryHandler(
            channel_callback,
            pattern=r"^del_channel:"
        )
    )


    # =====================================================
    # COMMUNITY MANAGEMENT
    # =====================================================

    application.add_handler(
        CallbackQueryHandler(
            community_callback,
            pattern=r"^(community_|community)"
        )
    )


    # =====================================================
    # SIGNAL
    # =====================================================

    application.add_handler(
        CallbackQueryHandler(
            signal_callback,
            pattern=r"^(toggle_channel:|toggle_community:|send_signal|send_signal_all|send_signal_communities|send_signal_all_communities|signal_preview)"
        )
    )


    # =====================================================
    # REPORT
    # =====================================================

    application.add_handler(
        CallbackQueryHandler(
            report_callback,
            pattern=r"^(toggle_report_channel:|report_)"
        )
    )


    # =====================================================
    # SIGNAL MANAGEMENT
    # =====================================================

    application.add_handler(
        CallbackQueryHandler(
            signal_manage_callback,
            pattern=r"^(manage_signal:|signal_hide_mode|signal_active:|signal_deactive:|signal_tp:|signal_reason:)"
        )
    )


    # =====================================================
    # REPLY
    # =====================================================

    application.add_handler(
        CallbackQueryHandler(
            reply_callback,
            pattern=r"^(reply_)"
        )
    )
    # =====================================================
    # BROADCAST
    # =====================================================

    application.add_handler(
        CallbackQueryHandler(
            broadcast_callback,
            pattern=r"^broadcast_"
        )
    )