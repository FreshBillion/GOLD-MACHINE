from config import SYMBOL
from data_fetcher import fetch_candles
from strategy import scan
from telegram_sender import send_signal
from positions import load_positions, save_positions, has_open_position, open_position


def run():
    positions = load_positions()

    if has_open_position(positions, SYMBOL):
        print(f"{SYMBOL} already has an open position — skipping scan.")
        return

    print(f"Scanning {SYMBOL}...")
    df = fetch_candles(SYMBOL)
    if df.empty:
        print("No data fetched — exiting.")
        return

    signal = scan(df)
    if not signal:
        print("No setup found this scan.")
        return

    existing = positions.get(SYMBOL)
    if existing and existing.get("last_signal_candle") == signal["candle_time"]:
        print(f"{SYMBOL}: already acted on this candle, skipping.")
        return

    print(f"Setup found: {signal['direction']} at {signal['entry']}")
    send_signal(signal)
    open_position(positions, signal)
    save_positions(positions)


if __name__ == "__main__":
    run()
