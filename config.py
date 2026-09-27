import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
TELEGRAM_PERSONAL_CHAT_ID = os.environ.get("TELEGRAM_PERSONAL_CHAT_ID")
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")

SYMBOL = "XAU/USD"
TIMEFRAME = "1h"
CANDLE_LIMIT = 300

POSITION_CHECK_TIMEFRAME = "1min"

# Engulfing pattern + prominence filter — backtested at prominence >= 20 across
# ~3 years / 8 periods of XAU/USD 1h data: 7 of 8 periods net positive
PROMINENCE_THRESHOLD = 20
MIN_ENGULF_RATIO = 1.0

# Each of the 3 legs is a fixed 0.01 lot (1 oz) position — this matches how
# the backtest computed dollar results directly from price distance
# Fixed position size — matches how the backtest computed dollar results
# directly from price distance (a $X move = $X per 0.01 lot / 1 oz)
POSITION_LOT_SIZE = 0.01
OZ_PER_LOT = 100

SL_DOLLARS = 12
TP1_DOLLARS = 12
TP2_DOLLARS = 24
TP3_DOLLARS = 36

STRATEGY_NAME_VEGA = "Vega"
STRATEGY_NAME_COMET = "Comet"

SOLDIERS_WICK_THRESHOLD = 0.20
SOLDIERS_SL_DOLLARS = 10
SOLDIERS_TP1_DOLLARS = 10
SOLDIERS_TP2_DOLLARS = 30
SOLDIERS_TP3_DOLLARS = 40

POSITION_EXPIRY_HOURS = 72
