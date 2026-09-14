import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# Markets to scan
SYMBOLS =  ["PAXG/USD"]

# Timeframe
TIMEFRAME = "1h"
CANDLE_LIMIT = 250

# Timeframe used specifically for checking open positions
POSITION_CHECK_TIMEFRAME = "1m"
POSITION_CHECK_LOOKBACK_MINUTES = 5   # always re-check a few minutes back to catch the current candle

# Strategy thresholds
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

# Stop-loss distance is ATR-based, but floored and capped as a % of price so it
# can't collapse to noise-level in quiet markets or blow out in wild ones
ATR_PERIOD = 14
ATR_SL_MULTIPLIER = 1.5
MIN_SL_PERCENT = 0.0015   # 0.15% of entry price
MAX_SL_PERCENT = 0.015    # 1.5% of entry price

# Take-profit targets, as multiples of the stop-loss distance (R) — these now
# scale with volatility the same way the stop does
TP1_R = 1.0
TP2_R = 2.0
TP3_R = 3.0

# Dollar risk per trade, based on signal strength — the bot sizes the position
# so the stop-loss distance above equals exactly this many dollars
RISK_DOLLARS_BY_LEVEL = {
    "A+": 7,
    "A": 6,
    "B": 5,
}

# Standard XAU/USD contract size — 1 lot = 100 oz on virtually every gold/CFD broker.
# Verify this matches your specific platform before trusting the lot number below.
LOT_SIZE = 100

# Signal tiers — how many of the 4 conditions (trend, MACD, RSI, volume) must align
LEVEL_LABELS = {
    4: "A+",
    3: "A",
    2: "B",
}
MIN_CONDITIONS_TO_SIGNAL = 2


# Gold/CFD platforms trade in lots, minimum size 0.01 lot (1 oz), moving in 0.01 steps.
# Verify this matches your specific platform.
OZ_PER_LOT = 100
MIN_LOT_SIZE = 0.01
LOT_STEP = 0.01

# After TP2 hits, move the stop-loss to entry (breakeven)
MOVE_SL_TO_BREAKEVEN_AFTER_TP2 = True

# Auto-close a signal as "expired" if neither a TP nor the SL is hit within this window
POSITION_EXPIRY_HOURS = 48
