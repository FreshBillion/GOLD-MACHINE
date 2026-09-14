import math
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

from config import (
    EMA_FAST, EMA_SLOW, RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL, VOLUME_MA_PERIOD, VOLUME_MULTIPLIER,
    ATR_PERIOD, ATR_SL_MULTIPLIER, MIN_SL_PERCENT, MAX_SL_PERCENT,
    TP1_R, TP2_R, TP3_R, RISK_DOLLARS_BY_LEVEL,
    OZ_PER_LOT, MIN_LOT_SIZE, LOT_STEP,
    LEVEL_LABELS, MIN_CONDITIONS_TO_SIGNAL
)


def add_indicators(df):
    df["ema_fast"] = EMAIndicator(df["close"], window=EMA_FAST).ema_indicator()
    df["ema_slow"] = EMAIndicator(df["close"], window=EMA_SLOW).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=RSI_PERIOD).rsi()
    macd = MACD(df["close"], window_fast=MACD_FAST, window_slow=MACD_SLOW, window_sign=MACD_SIGNAL)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["volume_ma"] = df["volume"].rolling(VOLUME_MA_PERIOD).mean()
    df["atr"] = AverageTrueRange(df["high"], df["low"], df["close"], window=ATR_PERIOD).average_true_range()
    return df


def score_direction(last, direction):
    matched = []
    if direction == "bull":
        if last["ema_fast"] > last["ema_slow"]:
            matched.append("Trend")
        if last["macd"] > last["macd_signal"]:
            matched.append("MACD")
        if 50 < last["rsi"] < RSI_OVERBOUGHT:
            matched.append("RSI")
    else:
        if last["ema_fast"] < last["ema_slow"]:
            matched.append("Trend")
        if last["macd"] < last["macd_signal"]:
            matched.append("MACD")
        if RSI_OVERSOLD < last["rsi"] < 50:
            matched.append("RSI")
    if last["volume"] > (last["volume_ma"] * VOLUME_MULTIPLIER):
        matched.append("Volume")
    return len(matched), matched


def check_setup(symbol, df):
    df = add_indicators(df)
    df.dropna(inplace=True)
    if df.empty:
        return None

    last = df.iloc[-1]
    bull_score, bull_matched = score_direction(last, "bull")
    bear_score, bear_matched = score_direction(last, "bear")

    if bull_score == bear_score or max(bull_score, bear_score) < MIN_CONDITIONS_TO_SIGNAL:
        return None

    if bull_score > bear_score:
        direction, score, matched = "BUY", bull_score, bull_matched
    else:
        direction, score, matched = "SELL", bear_score, bear_matched

    level = LEVEL_LABELS.get(score, "B")
    entry = last["close"]
    atr = last["atr"]

    atr_distance = atr * ATR_SL_MULTIPLIER
    min_distance = entry * MIN_SL_PERCENT
    max_distance = entry * MAX_SL_PERCENT
    stop_distance = max(min_distance, min(atr_distance, max_distance))

    target_risk = RISK_DOLLARS_BY_LEVEL.get(level, 5)
    raw_oz = target_risk / stop_distance
    raw_lots = raw_oz / OZ_PER_LOT
    position_size_lots = round(max(MIN_LOT_SIZE, math.ceil(raw_lots / LOT_STEP) * LOT_STEP), 2)
    position_size_oz = round(position_size_lots * OZ_PER_LOT, 4)
    risk_dollars = round(position_size_oz * stop_distance, 2)  # real risk after rounding to a tradable lot

    tp1_distance = stop_distance * TP1_R
    tp2_distance = stop_distance * TP2_R
    tp3_distance = stop_distance * TP3_R

    if direction == "BUY":
        stop_loss = entry - stop_distance
        tp1, tp2, tp3 = entry + tp1_distance, entry + tp2_distance, entry + tp3_distance
    else:
        stop_loss = entry + stop_distance
        tp1, tp2, tp3 = entry - tp1_distance, entry - tp2_distance, entry - tp3_distance

    return {
        "symbol": symbol,
        "direction": direction,
        "level": level,
        "conditions_met": matched,
        "entry": round(entry, 4),
        "stop_loss": round(stop_loss, 4),
        "tp1": round(tp1, 4),
        "tp2": round(tp2, 4),
        "tp3": round(tp3, 4),
        "position_size": position_size_oz,
        "position_size_lots": position_size_lots,
        "risk_dollars": risk_dollars,
        "rsi": round(last["rsi"], 1),
    }


def scan_all(data):
    signals = []
    for symbol, df in data.items():
        result = check_setup(symbol, df)
        if result:
            signals.append(result)
    return signals
