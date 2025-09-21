# app/api/endpoints.py
# Purpose: Public API endpoints (intent routing, price lookup, alert creation, news).
# Style: minimal, robust, LLM-safe. Comments in English.

from __future__ import annotations

from enum import IntEnum
import re
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.schema import PromptRequest
from app.api.services import analizar_web, crear_alerta_from_llm
from app.core.llm import ask_llm
from app.core.market import get_last_price, get_changes
from app.core.news import get_ticker_news
from app.core.symbols import resolve_symbol
from app.db.database import SessionLocal

router = APIRouter()


# ------------------------------------------------------------------------------
# DB session per request
# ------------------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------------------------------------------------------
# Intent classification (deterministic first, LLM as fallback -> numeric code)
# ------------------------------------------------------------------------------
class Intent(IntEnum):
    GENERAL = 0
    FINANCIERO = 1
    ALERTA = 2


def _looks_like_alert(text: str) -> bool:
    """Heuristic: if it smells like an alert rule, return True."""
    t = (text or "").lower()
    if re.search(r"\b(alerta|alertame|av[íi]same|avisame|notifica|notificar)\b", t):
        return True
    # “si/cuando ... sube/baja/supera/cae ... <número>”
    return bool(re.search(r"\b(si|cuando)\b.*\b(sube|baja|supera|cae|rompe|cruza)\b.*\d", t))


def _looks_like_financial(text: str) -> bool:
    """Heuristic: price talk or ticker-like token present."""
    t = (text or "").lower()
    if re.search(r"\b(precio|cotiza|cotizaci[óo]n|quote|price|valor)\b", t):
        return True
    if re.search(r"\b[A-Z0-9.\-]{2,12}\b", (text or "").upper()):
        return True
    return False


async def _classify_intent(text: str) -> Intent:
    """Deterministic heuristics first; otherwise ask LLM for a single digit 0/1/2."""
    if _looks_like_alert(text):
        return Intent.ALERTA
    if _looks_like_financial(text):
        return Intent.FINANCIERO

    prompt = (
        "Clasifica la consulta en UNA sola categoría y devuelve SOLO un dígito:\n"
        "0 = general\n1 = financiero\n2 = alerta\n\n"
        f"Consulta: \"{text}\"\n"
        "Responde SOLO con 0 o 1 o 2."
    )
    raw = (await ask_llm(prompt)) or ""
    m = re.search(r"[0-2]", raw)
    if not m:
        return Intent.GENERAL
    try:
        return Intent(int(m.group(0)))
    except ValueError:
        return Intent.GENERAL


def _extract_symbolish(s: str) -> str | None:
    """Grab first SYMBOL-like token from an LLM reply (e.g., 'GOOGL (NASDAQ)')."""
    if not s:
        return None
    m = re.search(r"\b[A-Z0-9.\-]{1,12}\b", s.upper())
    return m.group(0) if m else None


# ------------------------------------------------------------------------------
# Main endpoint: /consulta
# ------------------------------------------------------------------------------
@router.post("/consulta")
async def consulta(data: PromptRequest, db: Session = Depends(get_db)):
    """
    Route user prompt:
      2) ALERTA     -> create alert (LLM JSON w/ strict mold + regex fallback)
      1) FINANCIERO -> resolve symbol, return price + deltas
      0) GENERAL    -> LLM-guided web analysis
    """
    prompt = (data.prompt or "").strip()
    intent = await _classify_intent(prompt)
    print(f"[intent] {intent.name} ({intent.value})")

    # --- FINANCIAL FLOW -------------------------------------------------------
    if intent == Intent.FINANCIERO:
        # 1) Try resolving directly from the user prompt (no LLM).
        ticker = resolve_symbol(prompt)

        # 2) If still unknown, ask LLM with strict examples; then sanitize & resolve again.
        if not ticker:
            llm_hint = await ask_llm(
                "Devuelve SOLO el ticker en mayúsculas, sin texto extra.\n"
                "Ejemplos:\n"
                "- 'precio de google' -> GOOGL\n"
                "- 'precio de alphabet' -> GOOGL\n"
                "- 'precio de bitcoin' -> BTC-USD\n"
                "- 'precio de tesla' -> TSLA\n"
                f"Pregunta: '{prompt}'\n"
                "Responde SOLO el ticker (ej: GOOGL)"
            )
            candidate = _extract_symbolish(llm_hint)
            ticker = resolve_symbol(candidate or "")

        if not ticker:
            return {"error": "No pude resolver el símbolo. Prueba con el ticker (ej. MSFT) o el nombre exacto."}

        snap = get_last_price(ticker)
        if snap.price is None:
            return {"error": f"No se pudo obtener el precio de {ticker}"}

        chg1h, chg24h, chg7d = get_changes(ticker)
        return {
            "respuesta": f"Precio {snap.name} ({snap.symbol}): {round(snap.price, 2)} USD",
            "cambios": {"1h": chg1h, "24h": chg24h, "7d": chg7d},
        }

    # --- ALERT FLOW -----------------------------------------------------------
    if intent == Intent.ALERTA:
        # LLM returns strict JSON mold; service normalizes/validates & persists.
        return await crear_alerta_from_llm(prompt, db)

    # --- GENERAL FLOW ---------------------------------------------------------
    resultado = await analizar_web(prompt)
    return {"respuesta": resultado}


# ------------------------------------------------------------------------------
# Debug & utilities
# ------------------------------------------------------------------------------
@router.get("/debug/alertas")
def listar_alertas(db: Session = Depends(get_db)):
    """List stored alerts (debug)."""
    from app.db.models import Alerta
    rows = db.query(Alerta).all()
    return [
        {
            "id": a.id,
            "simbolo": a.simbolo,
            "condicion": a.condicion,
            "umbral": a.umbral,
            "notificado": a.notificado,
        }
        for a in rows
    ]


@router.get("/news/{q}")
def news_ticker(q: str):
    """Return recent headlines related to a symbol/name (API-first + RSS fallback)."""
    return {"ticker": q.upper(), "news": get_ticker_news(q, limit=5)}
