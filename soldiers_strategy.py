# soldiers_strategy.py — "Comet": Three White Soldiers (bullish only). Standard
# rule: each candle closes higher than the previous candle's CLOSE. Wick filter
# caps upper wick at 20% of candle range. Backtested: 53 signals/~2.9yrs at
# SL $10/TP1 $10/TP2 $30/TP3 $40, 3-position expectancy $14.91.

from config import (
    SOLDIERS_WICK_THRESHOLD, SOLDIERS_SL_DOLLARS,
    SOLDIERS_TP1_DOLLARS, SOLDIERS_TP2_DOLLARS, SOLDIERS_TP3_DOLLARS,
    STRATEGY_NAME_COMET
)

POSITION_KEY = "XAU/USD-COMET"   # distinct tracking key — never collides with Vega's "XAU/USD"
MARKET_SYMBOL = "XAU/USD"


def scan(df) -> dict | None:
    if len(df) < 4:
        return None

    i = len(df) - 1
    c1 = df.iloc[i - 2]
    c2 = df.iloc[i - 1]
    c3 = df.iloc[i]
    candles = [c1, c2, c3]

    if not all(c["close"] > c["open"] for c in candles):
        return None

    c1_lo, c1_hi = min(c1["open"], c1["close"]), max(c1["open"], c1["close"])
    if not (c1_lo <= c2["open"] <= c1_hi and c2["open"] > c1["open"]):
        return None

    c2_lo, c2_hi = min(c2["open"], c2["close"]), max(c2["open"], c2["close"])
    if not (c2_lo <= c3["open"] <= c2_hi and c3["open"] > c2["open"]):
        return None

    if not (c2["close"] > c1["close"] and c3["close"] > c2["close"]):
        return None

    for c in candles:
        rng = c["high"] - c["low"]
        if rng <= 0 or (c["high"] - c["close"]) > SOLDIERS_WICK_THRESHOLD * rng:
            return None

    entry = c3["close"]
    stop_loss = entry - SOLDIERS_SL_DOLLARS
    tp1 = entry + SOLDIERS_TP1_DOLLARS
    tp2 = entry + SOLDIERS_TP2_DOLLARS
    tp3 = entry + SOLDIERS_TP3_DOLLARS

    return {
        "symbol": POSITION_KEY,
        "market_symbol": MARKET_SYMBOL,
        "strategy_name": STRATEGY_NAME_COMET,
        "direction": "BUY",
        "entry": round(entry, 4),
        "stop_loss": round(stop_loss, 4),
        "tp1": round(tp1, 4),
        "tp2": round(tp2, 4),
        "tp3": round(tp3, 4),
        "candle_time": df.index[i].isoformat(),
    }
