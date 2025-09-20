# app/core/notifications.py
import requests
from app.core.config import settings

def enviar_telegram_mensaje(texto: str):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Mensaje enviado por Telegram")
        else:
            print(f"❌ Error al enviar Telegram: {response.text}")
    except Exception as e:
        print(f"⚠️ Excepción en Telegram: {e}")
