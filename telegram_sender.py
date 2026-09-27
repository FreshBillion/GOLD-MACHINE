# telegram_sender.py — formats/sends signals for both Vega (engulfing) and
# Comet (Soldiers), plus shared TP/SL follow-up updates tagged by strategy.

import requests
from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID,
    SL_DOLLARS, TP1_DOLLARS, TP2_DOLLARS, TP3_DOLLARS, STRATEGY_NAME_VEGA,
    SOLDIERS_SL_DOLLARS, SOLDIERS_TP1_DOLLARS, SOLDIERS_TP2_DOLLARS, SOLDIERS_TP3_DOLLARS,
    STRATEGY_NAME_COMET
)


def _send(message: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHANNEL_ID, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Telegram send failed: {response.text}")
    return response.status_code == 200


def format_vega_signal(signal: dict) -> str:
    emoji = "🟢" if signal["direction"] == "BUY" else "🔴"
    return (
        f"{emoji} *{STRATEGY_NAME_VEGA} SETUP — {signal['direction']}* — {signal['market_symbol']}\n\n"
        f"Entry: `{signal['entry']}`\n"
        f"Stop Loss: `{signal['stop_loss']}`  (-${SL_DOLLARS})\n\n"
        f"TP1: `{signal['tp1']}`  (+${TP1_DOLLARS})\n"
        f"TP2: `{signal['tp2']}`  (+${TP2_DOLLARS})\n"
        f"TP3: `{signal['tp3']}`  (+${TP3_DOLLARS})\n\n"
        f"See pinned message for position sizing options.\n\n"
        f"_Not financial advice. Trade at your own risk._"
    )


def send_vega_signal(signal: dict) -> bool:
    return _send(format_vega_signal(signal))


def format_comet_signal(signal: dict) -> str:
    return (
        f"🟢 *{STRATEGY_NAME_COMET} SETUP — {signal['direction']}* — {signal['market_symbol']}\n\n"
        f"Entry: `{signal['entry']}`\n"
        f"Stop Loss: `{signal['stop_loss']}`  (-${SOLDIERS_SL_DOLLARS})\n\n"
        f"TP1: `{signal['tp1']}`  (+${SOLDIERS_TP1_DOLLARS})\n"
        f"TP2: `{signal['tp2']}`  (+${SOLDIERS_TP2_DOLLARS})\n"
        f"TP3: `{signal['tp3']}`  (+${SOLDIERS_TP3_DOLLARS})\n\n"
        f"See pinned message for position sizing options.\n\n"
        f"_Not financial advice. Trade at your own risk._"
    )


def send_comet_signal(signal: dict) -> bool:
    return _send(format_comet_signal(signal))


EVENT_MESSAGES = {
    "tp1_hit": "🎯 *TP1 HIT*",
    "tp2_hit": "🎯 *TP2 HIT* — stop moved to breakeven",
    "tp3_hit": "🏁 *TP3 HIT — Trade closed, full target reached*",
    "stop_loss": "🛑 *STOP LOSS HIT — Trade closed*",
    "breakeven": "⚪ *Stopped at breakeven — Trade closed, no loss*",
    "expired": "⌛ *Signal expired — closed with no TP or SL hit*",
    "breakeven_set": None,
}


def _sl_dollars_for(pos: dict) -> float:
    return SOLDIERS_SL_DOLLARS if pos.get("strategy_name") == STRATEGY_NAME_COMET else SL_DOLLARS


def _tp_dollars_for(pos: dict, tp_key: str) -> float:
    if pos.get("strategy_name") == STRATEGY_NAME_COMET:
        return {"tp1_hit": SOLDIERS_TP1_DOLLARS, "tp2_hit": SOLDIERS_TP2_DOLLARS,
                "tp3_hit": SOLDIERS_TP3_DOLLARS}[tp_key]
    return {"tp1_hit": TP1_DOLLARS, "tp2_hit": TP2_DOLLARS, "tp3_hit": TP3_DOLLARS}[tp_key]


def send_update(event: dict, pos: dict) -> bool:
    if EVENT_MESSAGES.get(event["type"]) is None:
        return True

    header = EVENT_MESSAGES[event["type"]]
    extra = ""
    if event["type"] in ("tp1_hit", "tp2_hit", "tp3_hit"):
        extra = f"  (+${_tp_dollars_for(pos, event['type'])})"
    elif event["type"] == "stop_loss":
        extra = f"  (-${_sl_dollars_for(pos)})"

    strategy_tag = pos.get("strategy_name", "")
    message = (
        f"{header}{extra}\n\n"
        f"{strategy_tag} — {event['symbol']} — {pos['direction']}\n"
        f"Entry: `{pos['entry']}`\n"
        f"Price now: `{round(event['price'], 4)}`"
    )
    return _send(message)
