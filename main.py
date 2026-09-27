# main.py — fetches XAU/USD 1h candles once, runs both Vega and Comet against it.

from config import SYMBOL
from data_fetcher import fetch_candles
from telegram_sender import send_vega_signal, send_comet_signal
from positions import load_positions, save_positions, has_open_position, open_position

import strategy as vega_strategy
import soldiers_strategy as comet_strategy


def _try_strategy(positions, position_key, scan_fn, send_fn, df, label):
    if has_open_position(positions, position_key):
        print(f"{label}: already has an open position — skipping.")
        return

    signal = scan_fn(df)
    if not signal:
        print(f"{label}: no setup found this scan.")
        return

    existing = positions.get(position_key)
    if existing and existing.get("last_signal_candle") == signal["candle_time"]:
        print(f"{label}: already acted on this candle, skipping.")
        return

    print(f"{label}: setup found — {signal['direction']} at {signal['entry']}")
    send_fn(signal)
    open_position(positions, signal)


def run():
    positions = load_positions()

    print(f"Fetching {SYMBOL}...")
    df = fetch_candles(SYMBOL)
    if df.empty:
        print("No data fetched — exiting.")
        return

    _try_strategy(positions, SYMBOL, vega_strategy.scan, send_vega_signal, df, "Vega")
    _try_strategy(positions, comet_strategy.POSITION_KEY, comet_strategy.scan, send_comet_signal, df, "Comet")

    save_positions(positions)


if __name__ == "__main__":
    run()
