# -*- coding: utf-8 -*-
from app.services import servis_symbol_manager as symbol_manager
from app.services.servis_user_manager import load_users
async def load_data(application):

    application.bot_data["symbols"] = symbol_manager.load_symbols()

    application.bot_data["users"] = load_users()
def save_symbols(application):

    symbols = application.bot_data.get("symbols", {})

    symbol_manager.save_symbols(symbols)