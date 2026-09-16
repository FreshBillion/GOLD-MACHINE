import os
TELEGRAM_PERSONAL_CHAT_ID = os.environ.get("TELEGRAM_PERSONAL_CHAT_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

SYMBOLS = ["PAXG/USD"]

TIMEFRAME = "1h"
CANDLE_LIMIT = 250

POSITION_CHECK_TIMEFRAME = "1m"

EMA_FAST = 50
EMA_SLOW = 200
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
VOLUME_MA_PERIOD = 20
VOLUME_MULTIPLIER = 1.5

# Tightened vs. crypto — PAXG's ATR runs wide relative to typical gold stop sizes
ATR_PERIOD = 14
ATR_SL_MULTIPLIER = 1.0
MIN_SL_PERCENT = 0.001    # ~$4 on gold near $4,300
MAX_SL_PERCENT = 0.004    # ~$17 on gold near $4,300

TP1_R = 1.0
TP2_R = 2.0
TP3_R = 3.0

RISK_DOLLARS_BY_LEVEL = {
    "A+": 7,
    "A": 6,
    "B": 5,
}

# Gold/CFD platforms trade in lots, minimum size 0.01 lot (1 oz), moving in 0.01 steps.
# Verify this matches your specific platform.
OZ_PER_LOT = 100
MIN_LOT_SIZE = 0.01
LOT_STEP = 0.01

LEVEL_LABELS = {
    4: "A+",
    3: "A",
    2: "B",
}
MIN_CONDITIONS_TO_SIGNAL = 2

MOVE_SL_TO_BREAKEVEN_AFTER_TP2 = True

POSITION_EXPIRY_HOURS = 48
