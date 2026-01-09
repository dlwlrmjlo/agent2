# app/core/notifications.py
import requests
from app.core.config import settings

def enviar_telegram_mensaje(texto: str, chat_id: str | None = None, parse_mode: str | None = None):
    token = settings.TELEGRAM_BOT_TOKEN
    chat = chat_id or settings.TELEGRAM_CHAT_ID
    if not token or not chat:
        print("ℹ️ Telegram no configurado (TOKEN/CHAT_ID)."); return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat, "text": texto}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print("❌ Telegram:", r.text)
    except Exception as e:
        print("⚠️ Telegram exception:", e)
