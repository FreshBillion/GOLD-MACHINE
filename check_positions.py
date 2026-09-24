# check_positions.py — checks open positions by replaying candle history since the last
# confirmed checkpoint (strictly forward only). Only uses fully-closed candles.

import re
from datetime import datetime, timedelta

from data_fetcher import fetch_since
from positions import load_positions, save_positions, check_position
from telegram_sender import send_update
from config import POSITION_CHECK_TIMEFRAME


def _timeframe_to_timedelta(tf: str) -> timedelta:
    match = re.match(r"(\d+)([a-zA-Z]+)", tf)
    value, unit = int(match.group(1)), match.group(2).lower()
    if unit in ("m", "min"):
        return timedelta(minutes=value)
    if unit in ("h", "hour"):
        return timedelta(hours=value)
    if unit in ("d", "day"):
        return timedelta(days=value)
    return timedelta(minutes=value)


def _drop_forming_candle(candles, timeframe: str):
    if candles.empty:
        return candles
    duration = _timeframe_to_timedelta(timeframe)
    last_candle_end = candles.index[-1] + duration
    if datetime.utcnow() >= last_candle_end:
        return candles
    return candles.iloc[:-1]


def run():
    positions = load_positions()
    open_symbols = [s for s, p in positions.items() if p.get("status") == "open"]

    if not open_symbols:
        print("No open positions to check.")
        return

    for symbol in open_symbols:
        pos = positions[symbol]

        last_checked_ms = int(datetime.fromisoformat(pos.get("last_checked", pos["opened_at"])).timestamp() * 1000)
        since_ms = last_checked_ms + 1

        candles = fetch_since(symbol, since_ms, timeframe=POSITION_CHECK_TIMEFRAME)
        candles = _drop_forming_candle(candles, POSITION_CHECK_TIMEFRAME)

        if candles.empty:
            print(f"{symbol}: no new closed candles since last check.")
            continue

        events = check_position(symbol, pos, candles)
        for event in events:
            send_update(event, pos)

        if events:
            print(f"{symbol}: {[e['type'] for e in events]}")
        else:
            print(f"{symbol}: no TP/SL touched in this window.")

    save_positions(positions)


if __name__ == "__main__":
    run()
