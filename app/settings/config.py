import os

from datetime import time
from zoneinfo import ZoneInfo
TOKEN = "توکن"


def _get_admin_id() -> int:
    env_id = os.environ.get("ADMIN_ID", "").strip()
    if not env_id:
        raise RuntimeError(
            "ADMIN_ID is not set. "
            "Add ADMIN_ID=<your-telegram-id> to .env"
        )
    try:
        return int(env_id)
    except ValueError:
        raise RuntimeError(
            f"ADMIN_ID must be a number, got: {env_id!r}"
        )


ADMIN_ID = _get_admin_id()
SYMBOLS_PER_PAGE = 6
DAILY_REPORT_HOUR = 23
DAILY_REPORT_MINUTE = 59
DAILY_REPORT_TIMEZONE = ZoneInfo("Asia/Tehran")

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


# =========================================================
# ATOMIC WRITE HELPER
# =========================================================

import json
import tempfile


def atomic_json_write(filepath, data):
    """
    نوشتن ایمن JSON — اول در فایل tmp مینویسه
    بعد rename میکنه.
    اگه حین نوشتن کرش بشه، فایل اصلی سالم میمونه.
    """
    dir_path = os.path.dirname(str(filepath))
    os.makedirs(dir_path, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(
        dir=dir_path,
        suffix=".tmp"
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        os.replace(tmp_path, str(filepath))

    except BaseException:
        # اگه خطا خورد، فایل tmp رو پاک کن
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise