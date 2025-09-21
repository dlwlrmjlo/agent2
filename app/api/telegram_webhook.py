# app/api/telegram_webhook.py
# Minimal webhook: route text to /consulta and reply; ignore callbacks for ahora.

from fastapi import APIRouter, Request, HTTPException
import requests
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import SessionLocal
from app.models.schema import PromptRequest
from app.api.endpoints import consulta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def _tg(method: str, payload: dict):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{method}"
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print("❌ Telegram:", r.text)
    except Exception as e:
        print("⚠️ Telegram exception:", e)

@router.post("/webhook/telegram")
async def recibir_mensaje(request: Request, token: str | None = None):
    if settings.WEBHOOK_SECRET and token != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="invalid webhook token")

    data = await request.json()
    if "message" not in data:
        return {"ok": True}  # ignore non-text events

    chat_id = str(data["message"]["chat"]["id"])
    text = data["message"].get("text") or ""
    if not text:
        return {"ok": True}

    db: Session = next(get_db())
    resp = await consulta(PromptRequest(prompt=text), db)
    msg = resp.get("respuesta") if isinstance(resp, dict) else str(resp)
    _tg("sendMessage", {"chat_id": chat_id, "text": msg})
    return {"ok": True}
