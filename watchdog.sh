#!/bin/bash
APP_DIR="/home/giftshop/segnallbot"
PYTHON="/home/giftshop/virtualenv/segnallbot/3.12/bin/python3.12_bin"
BOT="$APP_DIR/bot.py"
LOG="$APP_DIR/watchdog.log"
cd "$APP_DIR" || exit 1
if pgrep -f "^$PYTHON.*bot\.py" > /dev/null 2>&1; then
    PID=$(pgrep -f "^$PYTHON.*bot\.py" | head -n 1)
    echo "$(date "+%Y-%m-%d %H:%M:%S") - BOT OK - PID=$PID" >> "$LOG"
else
    echo "$(date "+%Y-%m-%d %H:%M:%S") - BOT DOWN - STARTING..." >> "$LOG"
    nohup "$PYTHON" -u "$BOT" >> "$APP_DIR/bot.log" 2>&1 < /dev/null &
    NEWPID=$!
    echo "$NEWPID" > "$APP_DIR/bot.pid"
    echo "$(date "+%Y-%m-%d %H:%M:%S") - BOT STARTED - PID=$NEWPID" >> "$LOG"
fi
