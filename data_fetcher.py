# data_fetcher.py — pulls candle (OHLC) data from Twelve Data for real XAU/USD gold prices
# timezone is forced to UTC explicitly — Twelve Data defaults to exchange-local time otherwise,
# which silently breaks every "since last check" calculation in this codebase

import requests
import pandas as pd
from datetime import datetime
from config import CANDLE_LIMIT, TIMEFRAME, TWELVE_DATA_API_KEY

BASE_URL = "https://api.twelvedata.com/time_series"


def _parse_response(data: dict) -> pd.DataFrame:
    if "values" not in data:
        raise RuntimeError(f"Twelve Data error: {data}")

    df = pd.DataFrame(data["values"])
    df["timestamp"] = pd.to_datetime(df["datetime"])
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)
    df["volume"] = df["volume"].astype(float) if "volume" in df.columns else 0.0

    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    df.set_index("timestamp", inplace=True)
    df.sort_index(inplace=True)
    return df


def fetch_candles(symbol: str) -> pd.DataFrame:
    params = {
        "symbol": symbol,
        "interval": TIMEFRAME,
        "outputsize": CANDLE_LIMIT,
        "timezone": "UTC",
        "apikey": TWELVE_DATA_API_KEY,
    }
    response = requests.get(BASE_URL, params=params)
    return _parse_response(response.json())


def fetch_since(symbol: str, since_ms: int, timeframe: str = "1min") -> pd.DataFrame:
    start_date = datetime.utcfromtimestamp(since_ms / 1000).strftime("%Y-%m-%d %H:%M:%S")
    params = {
        "symbol": symbol,
        "interval": timeframe,
        "start_date": start_date,
        "timezone": "UTC",
        "apikey": TWELVE_DATA_API_KEY,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    if "values" not in data:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    return _parse_response(data)


def fetch_all(symbols: list) -> dict:
    data = {}
    for symbol in symbols:
        try:
            data[symbol] = fetch_candles(symbol)
        except Exception as e:
            print(f"Failed to fetch {symbol}: {e}")
    return data
