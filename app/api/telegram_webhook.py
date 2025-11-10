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
            print("[Telegram HTTP]:", r.text)
    except Exception as e:
        print("[Telegram exception]:", e)

def _format_reply(resp) -> str:
    """Best-effort text formatter for various API responses.
    - If dict with 'respuesta' -> return it.
    - If EXPLAIN payload -> bullets or general summary.
    - If NEWS payload -> list top titles.
    - Else stringify compactly.
    """
    try:
        if isinstance(resp, dict):
            # direct text
            if resp.get("respuesta"):
                return str(resp.get("respuesta"))

            # explain payload — prefer the market brief if available
            if resp.get("summary_bullets") or resp.get("summary_general"):
                ticker = resp.get("ticker") or ""
                brief = resp.get("summary_general")
                if isinstance(brief, str) and brief.strip():
                    ev = resp.get("event") or {}
                    hit = ev.get("hit")
                    window = ev.get("window")
                    d15 = ev.get("delta_15m")
                    d60 = ev.get("delta_60m")
                    shock_txt = "Sí" if hit else "No"
                    win_txt = f" ({window})" if hit and window else ""
                    d15_txt = f"{d15:+.2f}%" if isinstance(d15, (int, float)) else "n/d"
                    d60_txt = f"{d60:+.2f}%" if isinstance(d60, (int, float)) else "n/d"
                    d24 = ev.get("delta_24h")
                    d7  = ev.get("delta_7d")
                    d24_txt = f"{d24:+.2f}%" if isinstance(d24, (int, float)) else "n/d"
                    d7_txt  = f"{d7:+.2f}%" if isinstance(d7, (int, float)) else "n/d"
                    header = (
                        f"{ticker}\n"
                        f"A continuación te dejo los datos del stock {ticker}.\n"
                        f"Shock: {shock_txt}{win_txt} | Δ15m={d15_txt} | Δ60m={d60_txt} | 24h={d24_txt} | 7d={d7_txt}\n\n"
                    )
                    return (header + brief.strip()).strip()
                bullets = resp.get("summary_bullets")
                if isinstance(bullets, list) and bullets:
                    ev = resp.get("event") or {}
                    hit = ev.get("hit")
                    window = ev.get("window")
                    d15 = ev.get("delta_15m")
                    d60 = ev.get("delta_60m")
                    shock_txt = "Sí" if hit else "No"
                    win_txt = f" ({window})" if hit and window else ""
                    d15_txt = f"{d15:+.2f}%" if isinstance(d15, (int, float)) else "n/d"
                    d60_txt = f"{d60:+.2f}%" if isinstance(d60, (int, float)) else "n/d"
                    d24 = ev.get("delta_24h")
                    d7  = ev.get("delta_7d")
                    d24_txt = f"{d24:+.2f}%" if isinstance(d24, (int, float)) else "n/d"
                    d7_txt  = f"{d7:+.2f}%" if isinstance(d7, (int, float)) else "n/d"
                    header = [
                        f"{ticker}",
                        f"A continuación te dejo los datos del stock {ticker}.",
                        f"Shock: {shock_txt}{win_txt} | Δ15m={d15_txt} | Δ60m={d60_txt} | 24h={d24_txt} | 7d={d7_txt}",
                        "",
                    ]
                    lines = header + [ (b if str(b).lstrip().startswith('-') else f"- {b}") for b in bullets ]
                    return "\n".join(lines)
                if isinstance(bullets, str) and bullets.strip():
                    ev = resp.get("event") or {}
                    hit = ev.get("hit")
                    window = ev.get("window")
                    d15 = ev.get("delta_15m")
                    d60 = ev.get("delta_60m")
                    shock_txt = "Sí" if hit else "No"
                    win_txt = f" ({window})" if hit and window else ""
                    d15_txt = f"{d15:+.2f}%" if isinstance(d15, (int, float)) else "n/d"
                    d60_txt = f"{d60:+.2f}%" if isinstance(d60, (int, float)) else "n/d"
                    d24 = ev.get("delta_24h")
                    d7  = ev.get("delta_7d")
                    d24_txt = f"{d24:+.2f}%" if isinstance(d24, (int, float)) else "n/d"
                    d7_txt  = f"{d7:+.2f}%" if isinstance(d7, (int, float)) else "n/d"
                    header = (
                        f"{ticker}\n"
                        f"A continuación te dejo los datos del stock {ticker}.\n"
                        f"Shock: {shock_txt}{win_txt} | Δ15m={d15_txt} | Δ60m={d60_txt} | 24h={d24_txt} | 7d={d7_txt}\n\n"
                    )
                    return (header + bullets.strip()).strip()

            # news payload
            news = resp.get("news")
            if isinstance(news, list):
                t = (resp.get("ticker") or "").upper()
                items = news[:5]
                lines = [f"Noticias {t}"] + [f"- {it.get('title','').strip()}" for it in items if it.get('title')]
                return "\n".join(lines) if len(lines) > 1 else f"Sin titulares para {t}"

        # fallback: compact string
        return str(resp)
    except Exception:
        return str(resp)

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
    msg = _format_reply(resp)
    _tg("sendMessage", {"chat_id": chat_id, "text": msg})
    return {"ok": True}


