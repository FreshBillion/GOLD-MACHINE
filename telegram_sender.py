# telegram_sender.py — formats and sends engulfing-pattern signals + TP/SL updates

import requests
from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, TELEGRAM_PERSONAL_CHAT_ID,
    SL_DOLLARS, TP1_DOLLARS, TP2_DOLLARS, TP3_DOLLARS
)


def _send(message: str, chat_id: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Telegram send failed ({chat_id}): {response.text}")
    return response.status_code == 200


def format_signal(signal: dict) -> str:
    emoji = "🟢" if signal["direction"] == "BUY" else "🔴"
    return (
        f"{emoji} *ENGULFING SETUP — {signal['direction']}* — {signal['symbol']}\n\n"
        f"Entry: `{signal['entry']}`\n"
        f"Stop Loss: `{signal['stop_loss']}`  (-${SL_DOLLARS})\n\n"
        f"TP1: `{signal['tp1']}`  (+${TP1_DOLLARS})\n"
        f"TP2: `{signal['tp2']}`  (+${TP2_DOLLARS})\n"
        f"TP3: `{signal['tp3']}`  (+${TP3_DOLLARS})\n\n"
        f"See pinned message for position sizing options.\n\n"
        f"_Not financial advice. Trade at your own risk._"
    )


def send_signal(signal: dict) -> bool:
    public_ok = _send(format_signal(signal), TELEGRAM_CHANNEL_ID)
    if TELEGRAM_PERSONAL_CHAT_ID:
        _send(format_signal(signal), TELEGRAM_PERSONAL_CHAT_ID)
    return public_ok


EVENT_MESSAGES = {
    "tp1_hit": "🎯 *TP1 HIT*",
    "tp2_hit": "🎯 *TP2 HIT* — stop moved to breakeven",
    "tp3_hit": "🏁 *TP3 HIT — Trade closed, full target reached*",
    "stop_loss": "🛑 *STOP LOSS HIT — Trade closed*",
    "breakeven": "⚪ *Stopped at breakeven — Trade closed, no loss*",
    "expired": "⌛ *Signal expired — closed with no TP or SL hit*",
    "breakeven_set": None,
}

EVENT_DOLLARS = {"tp1_hit": TP1_DOLLARS, "tp2_hit": TP2_DOLLARS, "tp3_hit": TP3_DOLLARS}


def send_update(event: dict, pos: dict) -> bool:
    if EVENT_MESSAGES.get(event["type"]) is None:
        return True

    header = EVENT_MESSAGES[event["type"]]
    extra = ""
    if event["type"] in EVENT_DOLLARS:
        extra = f"  (+${EVENT_DOLLARS[event['type']]})"
    elif event["type"] == "stop_loss":
        extra = f"  (-${SL_DOLLARS})"

    message = (
        f"{header}{extra}\n\n"
        f"{event['symbol']} — {pos['direction']}\n"
        f"Entry: `{pos['entry']}`\n"
        f"Price now: `{round(event['price'], 4)}`"
    )
    return _send(message, TELEGRAM_CHANNEL_ID)
