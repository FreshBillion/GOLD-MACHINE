# strategy.py — detects Bullish/Bearish Engulfing patterns filtered by swing
# prominence. Backtested at prominence >= 20 over ~3 years of XAU/USD 1h data.

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from config import SYMBOL, PROMINENCE_THRESHOLD, MIN_ENGULF_RATIO, SL_DOLLARS, TP1_DOLLARS, TP2_DOLLARS, TP3_DOLLARS


def _compute_prominence(values):
    peaks, props = find_peaks(values, distance=1, prominence=0)
    prom = np.zeros(len(values))
    prom[peaks] = props["prominences"]
    return prom


def _build_signal(direction: str, entry: float, candle_time: str) -> dict:
    is_buy = direction == "BUY"
    stop_loss = entry - SL_DOLLARS if is_buy else entry + SL_DOLLARS
    tp1 = entry + TP1_DOLLARS if is_buy else entry - TP1_DOLLARS
    tp2 = entry + TP2_DOLLARS if is_buy else entry - TP2_DOLLARS
    tp3 = entry + TP3_DOLLARS if is_buy else entry - TP3_DOLLARS

    return {
        "symbol": SYMBOL,
        "direction": direction,
        "entry": round(entry, 4),
        "stop_loss": round(stop_loss, 4),
        "tp1": round(tp1, 4),
        "tp2": round(tp2, 4),
        "tp3": round(tp3, 4),
        "candle_time": candle_time,
    }


def scan(df: pd.DataFrame) -> dict | None:
    """
    Checks the last two fully-closed candles for a prominence-filtered engulfing
    setup. Candle 1 = most recently closed candle, Candle 2 = the one before it.
    Entry is taken at Candle 1's close, as a proxy for "open of the next candle"
    since this runs right after Candle 1 finishes forming.
    """
    if len(df) < 10:
        return None

    high_prom = _compute_prominence(df["high"].values)
    low_prom = _compute_prominence(-df["low"].values)

    i = len(df) - 1
    c1_open, c1_close = df["open"].iloc[i], df["close"].iloc[i]
    c2_open, c2_close = df["open"].iloc[i - 1], df["close"].iloc[i - 1]
    c1_body = abs(c1_close - c1_open)
    c2_body = abs(c2_close - c2_open)

    if c2_body == 0 or c1_body < MIN_ENGULF_RATIO * c2_body:
        return None

    candle_time = df.index[i].isoformat()
    entry = c1_close

    if c2_close > c2_open and c1_close < c1_open:
        if c1_open >= c2_close and c1_close <= c2_open:
            if max(high_prom[i - 1], high_prom[i]) >= PROMINENCE_THRESHOLD:
                return _build_signal("SELL", entry, candle_time)

    if c2_close < c2_open and c1_close > c1_open:
        if c1_open <= c2_close and c1_close >= c2_open:
            if max(low_prom[i - 1], low_prom[i]) >= PROMINENCE_THRESHOLD:
                return _build_signal("BUY", entry, candle_time)

    return None
