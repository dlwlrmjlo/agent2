# app/core/summarize.py
# Purpose: short driver bullets + general market brief (no investment advice).

from __future__ import annotations
from typing import List, Dict, Optional
from app.core.llm import ask_llm

# === Bullets por titulares (ya lo tenías) ====================================
_SUMMARY_SYS_PROMPT = """Eres un analista financiero conciso.
Resume SOLO con los datos entregados (título y fuente). Sin inventar cifras.
Máximo 5 líneas. Formato: viñetas de 1 línea.
Incluye el ticker al inicio y, si se infiere, el tipo de evento (earnings, regulación, M&A).
No des recomendaciones ni objetivos de precio.
"""

async def summarize_drivers(ticker: str, delta: float|None, window: str|None, drivers: List[Dict]) -> str:
    lines = []
    for d in drivers:
        t = (d.get("title") or "").strip()
        s = (d.get("source") or d.get("publisher") or "").strip()
        score = d.get("score")
        if t:
            lines.append(f"- {t} [{s}] (score={score})")
    facts = "\n".join(lines) if lines else "- (sin drivers)"
    delta_txt = f"{delta:+.2f}%" if isinstance(delta, (int,float)) else "n/d"
    prompt = (
        f"{_SUMMARY_SYS_PROMPT}\n\n"
        f"Ticker: {ticker}\n"
        f"Movimiento {window or 'n/d'}: {delta_txt}\n"
        f"Drivers:\n{facts}\n\n"
        "Entrega el resumen ahora."
    )
    return (await ask_llm(prompt)).strip()

# === Brief general “estado del mercado” ======================================
_MARKET_VIEW_SYS_PROMPT = """Eres un analista que redacta un BRIEF intradía.
Objetivo: sintetizar el estado GENERAL para un ticker dado.
Debes usar SOLO los datos provistos (variaciones y titulares). Nada de inventar cifras.
Formato: 5–7 líneas, en español claro, con:
1) contexto del movimiento (1h/24h/7d),
2) hipótesis plausibles (según titulares),
3) riesgos/contrapuntos,
4) sesgo cualitativo (alcista/bajista/neutro) y horizonte (intradía),
5) disclaimer final: “No es recomendación.”
Prohibido: recomendar comprar/vender, targets de precio, certezas.
"""

async def summarize_market_view(
    ticker: str,
    delta_1h: Optional[float],
    delta_24h: Optional[float],
    delta_7d: Optional[float],
    drivers: List[Dict],
    had_shock: bool
) -> str:
    # Compactamos hechos verificables para el LLM
    d1h  = "n/d" if delta_1h  is None else f"{delta_1h:+.2f}%"
    d24h = "n/d" if delta_24h is None else f"{delta_24h:+.2f}%"
    d7d  = "n/d" if delta_7d  is None else f"{delta_7d:+.2f}%"
    shock_txt = "sí" if had_shock else "no"

    # Seleccionamos los 3 mejores titulares como contexto
    lines = []
    for d in drivers[:3]:
        t = (d.get("title") or "").strip()
        s = (d.get("source") or d.get("publisher") or "").strip()
        inw = "en ventana" if d.get("in_window") else "fuera de ventana"
        if t:
            lines.append(f"- {t} [{s}; {inw}]")
    heads = "\n".join(lines) if lines else "- (sin titulares relevantes)"

    prompt = (
        f"{_MARKET_VIEW_SYS_PROMPT}\n\n"
        f"Ticker: {ticker}\n"
        f"Variaciones: 1h={d1h}, 24h={d24h}, 7d={d7d}\n"
        f"Shock detectado: {shock_txt}\n"
        f"TITULARES:\n{heads}\n\n"
        "Redacta el brief ahora."
    )
    return (await ask_llm(prompt)).strip()
