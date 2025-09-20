# app/api/telegram_webhook.py
from fastapi import APIRouter, Request
import requests
from app.core.config import settings
from app.models.schema import PromptRequest
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.api.endpoints import consulta


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def enviar_telegram_mensaje(texto: str, chat_id: str):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}
    requests.post(url, data=payload)


@router.post("/webhook/telegram")
async def recibir_mensaje(request: Request):
    data = await request.json()

    mensaje = data.get("message", {}).get("text")
    chat_id = data.get("message", {}).get("chat", {}).get("id")

    print(f"📥 Mensaje recibido de {chat_id}: {mensaje}")

    # Simulamos un request al endpoint de consulta
    prompt = PromptRequest(prompt=mensaje)
    db = next(get_db())
    respuesta = await consulta(prompt, db)

    # Extraemos la respuesta (puede ser string o dict)
    if isinstance(respuesta, dict):
        mensaje_respuesta = respuesta.get("respuesta") or respuesta.get("mensaje") or str(respuesta)
    else:
        mensaje_respuesta = str(respuesta)

    enviar_telegram_mensaje(mensaje_respuesta, chat_id)

    return {"ok": True}
