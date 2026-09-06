from datetime import time
from zoneinfo import ZoneInfo
TOKEN = "توکن"
ADMIN_ID = 163527680
SYMBOLS_PER_PAGE = 6
DAILY_REPORT_HOUR = 23
DAILY_REPORT_MINUTE = 59
DAILY_REPORT_TIMEZONE = ZoneInfo("Asia/Tehran")

import os

# ================== BASE PATH ==================

PROJECT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

DATA_DIR = os.path.join(
    PROJECT_DIR,
    "data"
)

# ================== JSON FILES ==================

COMMUNITIES_FILE = os.path.join(
    DATA_DIR,
    "communities.json"
)

CHANNELS_FILE = os.path.join(
    DATA_DIR,
    "channels.json"
)



from pathlib import Path


# =========================================================
# BASE / DATA PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"


# =========================================================
# USERS
# =========================================================

USERS_FILE = DATA_DIR / "users.json"


# =========================================================
# CHANNEL / COMMUNITY
# =========================================================

CHANNELS_FILE = DATA_DIR / "channels.json"

COMMUNITIES_FILE = DATA_DIR / "communities.json"


# =========================================================
# REPLY
# =========================================================

REPLY_TEXTS_FILE = DATA_DIR / "reply_texts.json"


# =========================================================
# SYMBOLS
# =========================================================

SYMBOLS_FILE = DATA_DIR / "symbols.json"


# =========================================================
# SIGNAL
# =========================================================

SIGNAL_LOG_FILE = DATA_DIR / "signals_log.json"

SIGNAL_TEXTS_FILE = DATA_DIR / "signal_texts.json"