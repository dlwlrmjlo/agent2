# app/api/endpoints.py
# Purpose: Public API endpoints (query routing, price lookup, alerts, news).
# Notes:
# - Uses LLM to classify intent (financial / general / alert) and extract ticker.
# - Replaces yfinance .info with fast, cached helpers from app.core.market.
# - Adds robust ticker normalization + regex fallback.
# - Keeps DB session dependency local and clean.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.schema import PromptRequest
from app.api.services import analizar_web, crear_alerta_from_llm
from app.core.llm import ask_llm
from app.db.database import SessionLocal
from app.core.market import get_last_price, get_changes
from app.core.news import get_ticker_news
import re

router = APIRouter()


# --- DB session dependency ----------------------------------------------------
def get_db():
    """Provide a scoped SQLAlchemy session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Main query endpoint ------------------------------------------------------
@router.post("/consulta")
async def consulta(data: PromptRequest, db: Session = Depends(get_db)):
    """
    Route user prompt:
      - financial  -> extract ticker -> price + changes
      - alert      -> create alert via LLM-structured JSON
      - general    -> web analysis (LLM + controlled scraping)
    """
    prompt = data.prompt.strip()

    # 1) Classify the intent using the LLM (strict 3-class output)
    pregunta = f"""Clasifica la siguiente consulta como:
- 'financiero' si es sobre acciones o criptomonedas,
- 'general' si no lo es,
- o 'alerta' si el usuario quiere configurar una condición o notificación.

Consulta: \"{prompt}\"
Responde solo con una palabra: financiero, general o alerta."""
    tipo = (await ask_llm(pregunta)).lower().strip()

    # 2) Financial flow: extract ticker and return fast price + deltas
    if tipo == "financiero":
        # Ask LLM for raw ticker candidate (can be noisy)
        ticker_raw = await ask_llm(
            f"Dime el ticker del activo mencionado en: '{prompt}'. "
            f"Responde únicamente con el símbolo sin explicar nada más."
        )
        print("🧠 Ticker crudo del LLM:", ticker_raw)

        # Normalize + basic aliases
        candidate = (ticker_raw or "").upper().strip()
        aliases = {
            # Crypto common names
            "BTC": "BTC-USD", "BITCOIN": "BTC-USD",
            "ETH": "ETH-USD", "ETHEREUM": "ETH-USD",
            # Blue chips (extend as needed)
            "TESLA": "TSLA", "APPLE": "AAPL", "AMAZON": "AMZN",
            "GOOGLE": "GOOGL", "ALPHABET": "GOOGL", "META": "META",
            "NVIDIA": "NVDA", "MICROSOFT": "MSFT",
        }
        if candidate in aliases:
            candidate = aliases[candidate]

        # Try a strict ticker pattern; fallback to scanning the original prompt
        match = re.search(r"\b[A-Z0-9.\-]{2,12}\b", candidate)
        if not match:
            match = re.search(r"\b[A-Z0-9.\-]{2,12}\b", prompt.upper())

        if not match:
            return {"error": f"No se pudo extraer un símbolo válido desde: '{ticker_raw}'"}

        ticker = match.group(0)
        if ticker == "BTC":  # normalize bare BTC to Yahoo symbol
            ticker = "BTC-USD"

        try:
            snap = get_last_price(ticker)  # cached, fast_info + history fallback
            if snap.price is None:
                return {"error": f"No se pudo obtener el precio de {ticker}"}

            chg1h, chg24h, chg7d = get_changes(ticker)
            return {
                "respuesta": f"Precio {snap.name} ({snap.symbol}): {snap.price} USD",
                "cambios": {"1h": chg1h, "24h": chg24h, "7d": chg7d},
            }
        except Exception as e:
            return {"error": f"No se pudo obtener el precio del activo: {e}"}

    # 3) Alert flow: structure alert via LLM and persist
    elif tipo == "alerta":
        return await crear_alerta_from_llm(prompt, db)

    # 4) General flow: controlled web analysis (LLM + scraping service)
    else:
        resultado = await analizar_web(prompt)
        return {"respuesta": resultado}


# --- Debug helpers ------------------------------------------------------------
@router.get("/debug/alertas")
def listar_alertas(db: Session = Depends(get_db)):
    """List current alerts for quick inspection (debug only)."""
    from app.db.models import Alerta
    alertas = db.query(Alerta).all()
    return [
        {
            "id": a.id,
            "simbolo": a.simbolo,
            "condicion": a.condicion,
            "umbral": a.umbral,
            "notificado": a.notificado,
        }
        for a in alertas
    ]


# --- Ticker news (API-first + fallback RSS) -----------------------------------
@router.get("/news/{ticker}")
def news_ticker(ticker: str):
    """Return recent headlines related to the given ticker."""
    return {"ticker": ticker.upper(), "news": get_ticker_news(ticker, limit=5)}
