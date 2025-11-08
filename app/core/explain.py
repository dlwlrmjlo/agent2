# app/core/explain.py
from __future__ import annotations
from typing import Dict, Any
from app.core.shocks import get_last_shock
from app.core.news_rank import rank_news_for_event
from app.core.symbols import resolve_symbol
from app.core.market import get_changes
from app.core.summarize import summarize_drivers, summarize_market_view  # <- nuevo

async def explain_move(q: str) -> Dict[str, Any]:
    symbol = resolve_symbol(q)
    if not symbol:
        return {"error": "No pude resolver el símbolo para explicar el movimiento."}

    shock = get_last_shock(symbol)
    # Traemos 1h/24h/7d para el brief general
    d1h, d24h, d7d = get_changes(symbol)

    # Siempre traemos drivers (si no hay shock, ventana más amplia)
    if shock.threshold_hit == "none":
        drivers = rank_news_for_event(symbol, shock.ts, window_before_min=180, window_after_min=0, limit=3)
        bullets  = await summarize_drivers(symbol, d1h, None, drivers)
        brief    = await summarize_market_view(symbol, d1h, d24h, d7d, drivers, had_shock=False)
        return {
            "ticker": symbol,
            "event": {
                "ts": shock.ts,
                "delta_15m": shock.delta_15m,
                "delta_60m": d1h,
                "hit": False
            },
            "drivers": drivers,
            "summary_bullets": bullets,
            "summary_general": brief,
            "message": "Sin shock detectado en la última hora.",
            "disclaimer": "Resumen informativo; no implica causalidad ni recomendación."
        }

    # Shock presente → ventana acotada y mismo esquema
    drivers = rank_news_for_event(symbol, shock.ts, limit=3)
    bullets = await summarize_drivers(symbol, d1h, shock.threshold_hit, drivers)
    brief   = await summarize_market_view(symbol, d1h, d24h, d7d, drivers, had_shock=True)
    return {
        "ticker": symbol,
        "event": {
            "ts": shock.ts,
            "delta_15m": shock.delta_15m,
            "delta_60m": d1h,
            "hit": True,
            "window": shock.threshold_hit
        },
        "drivers": drivers,
        "summary_bullets": bullets,
        "summary_general": brief,
        "disclaimer": "Explicaciones plausibles por proximidad temporal y fuente; no implica causalidad ni recomendación."
    }


from typing import List, Dict
from app.core.llm import ask_llm

def build_intraday_brief(symbol: str, top_news: List[Dict]) -> str:
    """
    Return a short intraday brief for `symbol` using `top_news` as context.
    If LLM is unavailable/empty, degrade gracefully with a human message.
    """
    titles = [f"- {n.get('title','').strip()}" for n in (top_news or []) if n.get("title")]
    context = "\n".join(titles[:5]) or "(sin titulares recientes)"

    prompt = (
        f"Resume en 3-5 líneas qué mueve hoy {symbol}. "
        f"No inventes. Usa solo estos titulares:\n{context}\n"
        "Devuelve texto plano, sin viñetas si no aportan."
    )

    raw = ask_llm(prompt) or ""
    text = (raw or "").strip()
    if not text:
        return f"No fue posible generar el brief ahora. Drivers poco concluyentes para {symbol}."
    return text