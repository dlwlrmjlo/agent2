# app/api/services.py
# All application services in one place:
# - Web analysis (LLM + light scraping)
# - Intent classification (heuristics + adapter/LLM 5 clases)
# - Alert creation (LLM strict mold + resolve_symbol + regex fallback)
# - Financial quote from prompt (resolve_symbol + market)

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.intent_adapter import predict as adapter_predict
from app.core.llm import ask_llm
from app.core.market import (
    get_changes,
    get_last_price,
    is_liquid_symbol,
    is_market_open,
)
from app.core.symbols import resolve_symbol
from app.db.models import Alerta


# ------------------------------------------------------------------------------
# Web search / analysis
# ------------------------------------------------------------------------------
async def search_google(query: str, num_results: int = 3) -> List[str]:
    from googlesearch import search

    return list(search(query, num_results=num_results))


async def scrape_website(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
    except Exception as e:
        return f"[ERROR scraping {url}]: {str(e)}"
    soup = BeautifulSoup(r.text, "lxml")
    return " ".join(p.get_text() for p in soup.find_all("p"))[:4000]


async def analizar_web(prompt: str) -> str:
    reformulado = await ask_llm(f"Reformula esta busqueda para Google: {prompt}")
    busqueda = (reformulado or "").strip() or prompt
    urls = await search_google(busqueda)
    contenidos = {u: await scrape_website(u) for u in urls}
    resumen = "\n\n".join([f"{u}:\n{t[:800]}" for u, t in contenidos.items()])
    prompt_final = f"""La consulta fue: {prompt}

Fuentes encontradas:

{resumen}

Redacta una respuesta clara y util en ESPAÑOL. Texto plano. NO uses formato markdown (negritas, cursivas) ni emojis. NO uses etiquetas HTML ni encierres links en < >."""
    raw = await ask_llm(prompt_final)
    return (raw or "").replace("<", "").replace(">", "")


# ------------------------------------------------------------------------------
# Intent classification (0=GENERAL,1=FIN,2=ALERTA,3=EXPLAIN,4=NEWS)
# ------------------------------------------------------------------------------
def _looks_like_news(text: str) -> bool:
    t = (text or "").lower()
    return bool(
        re.search(
            r"\b(noticia(s)?|titulares|headlines?|ultimas|que se dijo|rss|prensa|news)\b",
            t,
        )
    )


def _looks_like_explain(text: str) -> bool:
    t = (text or "").lower()
    patterns = [
        r"\bpor que\b",
        r"\bexplica(me)?\b",
        r"\bdrivers?\b",
        r"\brazones?\b",
        r"\bmotivo(s)?\b",
        r"\bcaus(a|as)\b",
        r"\bque paso\b",
        r"\bwhy\b",
        r"\bexplain\b",
    ]
    if any(re.search(p, t) for p in patterns):
        return True
    if re.search(r"\b(subio|bajo|cayo|salto|rally|sell[\s-]?off)\b", t) and re.search(
        r"\b(por que|que paso|why)\b", t
    ):
        return True
    return False


def _looks_like_alert(text: str) -> bool:
    t = (text or "").lower()
    if re.search(r"\b(alerta|alertame|avisame|notifica|notificar)\b", t):
        return True
    return bool(
        re.search(r"\b(si|cuando)\b.*\b(sube|baja|supera|cae|rompe|cruza)\b.*\d", t)
    )


def _looks_like_financial(text: str) -> bool:
    t = (text or "").lower()
    if re.search(r"\b(precio|cotiza|cotizacion|quote|price|valor)\b", t):
        return True
    return bool(re.search(r"\b[A-Z0-9.\-]{2,12}\b", (text or "").upper()))


async def classify_intent(text: str) -> int:  # type: ignore[no-redef]
    """
    0=general,1=fin,2=alerta,3=explain,4=news. Heuristicas -> adapter 5c -> LLM 5c (solo HYBRID si baja confianza).
    """
    t = (text or "").strip()
    mode = (settings.INTENT_MODE or "HYBRID").upper()
    conf_thr = float(getattr(settings, "INTENT_THRESHOLD", 0.80) or 0.80)

    # Heuristicas rapidas (SOLO en modo HYBRID para ahorrar computo)
    if mode == "HYBRID":
        if _looks_like_alert(t):
            print("⚡ [INTENT] HEAD: REGEX (Alert)")
            return 2
        if _looks_like_explain(t):
            print("⚡ [INTENT] HEAD: REGEX (Explain)")
            return 3
        if _looks_like_news(t):
            print("⚡ [INTENT] HEAD: REGEX (News)")
            return 4
        if _looks_like_financial(t):
            print("⚡ [INTENT] HEAD: REGEX (Financial)")
            return 1

    if mode == "ADAPTER":
        y, _ = adapter_predict(t)
        return int(y)

    if mode == "LLM":
        prompt = f"""Clasifica la consulta en UNA sola categoria y devuelve SOLO un digito:
0 = general
1 = financiero
2 = alerta
3 = explain
4 = news

- 'precio de tesla' -> 1
- 'avisame si TSLA cae de 300' -> 2
- 'que paso con SQM' -> 3
- 'noticias de AMD' -> 4
- 'contexto de SQM hoy' -> 0

Consulta: '{t}'
Responde SOLO con 0 o 1 o 2 o 3 o 4."""
        raw = (await ask_llm(prompt)) or ""
        m = re.search(r"[0-4]", raw)
        return int(m.group(0)) if m else 0

    y, p = adapter_predict(t)
    if p >= conf_thr:
        print(f"🔎 [INTENT] HEAD: ADAPTER (Conf: {p:.2f} >= {conf_thr}) -> Class {y}")
        return int(y)

    print(f"🧠 [INTENT] HEAD: LLM FALLBACK (Conf: {p:.2f} < {conf_thr})")
    prompt = f"""Clasifica la consulta en UNA sola categoria y devuelve SOLO un digito:
0 = general
1 = financiero
2 = alerta
3 = explain
4 = news

- 'precio de tesla' -> 1
- 'avisame si TSLA cae de 300' -> 2
- 'que paso con SQM' -> 3
- 'noticias de AMD' -> 4
- 'contexto de SQM hoy' -> 0

Consulta: '{t}'
Responde SOLO con 0 o 1 o 2 o 3 o 4."""
    raw = (await ask_llm(prompt)) or ""
    m = re.search(r"[0-4]", raw)
    return int(m.group(0)) if m else int(y)


# ------------------------------------------------------------------------------
# Shared utilities
# ------------------------------------------------------------------------------
def _extract_symbolish(s: str) -> Optional[str]:
    """First SYMBOL-like token from text/LLM reply (e.g., 'GOOGL (NASDAQ)')."""
    if not s:
        return None
    m = re.search(r"\b[A-Z0-9.\-]{1,12}\b", s.upper())
    return m.group(0) if m else None


_STOPWORDS_UP = {
    "QUE",
    "QUÉ",
    "DE",
    "DEL",
    "LA",
    "EL",
    "LOS",
    "LAS",
    "Y",
    "EN",
    "POR",
    "PARA",
    "CON",
    "AL",
    "UN",
    "UNA",
    "UNOS",
    "UNAS",
    "A",
    "SE",
    "LO",
    "SU",
    "SUS",
    "MI",
    "TUS",
    "SU",
    "NO",
    "SI",
    "CUANDO",
    "SUBE",
    "BAJA",
    "CAI",
    "CAE",
    "ROMPE",
    "CRUZA",
    "HOY",
    "AHORA",
    "CUANTO",
    "PRECIO",
}


def _extract_symbolish_tokens(s: str) -> List[str]:
    """All ticker-like tokens in text (uppercased), unordered."""
    if not s:
        return []
    t = (s or "").upper()
    toks = re.findall(r"[A-Z0-9.\-]{1,12}", t)
    # Keep hyphenated (e.g., BTC-USD), drop common stopwords
    out = []
    for tok in toks:
        u = tok.strip().upper()
        if not u or u in _STOPWORDS_UP:
            continue
        out.append(u)
    return out


async def resolve_ticker_from_prompt(prompt: str) -> Optional[str]:
    """
    Fast and robust ticker resolver for free-form prompts:
      1) Extract first SYMBOL-like token and try resolve_symbol.
      2) If fails, try resolve_symbol over the whole prompt (covers names).
      3) Fallback: ask LLM to answer ONLY a ticker, then resolve_symbol again.
    Returns an uppercase ticker or None.
    """
    txt = (prompt or "").strip()
    # 1) Try symbol-like tokens from right to left; require validation (no trust_direct)
    tokens = _extract_symbolish_tokens(txt)
    for cand in reversed(tokens):
        sym = resolve_symbol(cand, trust_direct=False)
        if sym:
            return sym
    # 2) try whole prompt (handles names via Yahoo search); require validation
    sym = resolve_symbol(txt, trust_direct=False)
    if sym:
        return sym
    # 3) LLM-only ticker extraction fallback
    prompt_llm = (
        "Devuelve SOLO el ticker en MAYUSCULAS si lo hay (ej: TSLA, GOOGL, AMD). "
        "Si no hay uno claro, devuelve vacio.\n"
        f'Consulta: "{txt}"\n'
        "Ticker:"
    )
    llm_hint = await ask_llm(prompt_llm) or ""
    candidate = _extract_symbolish(llm_hint)
    if not candidate:
        return None
    # Do NOT trust direct in this branch; require validation
    return resolve_symbol(candidate or "", trust_direct=False)


def _regex_fallback(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Deterministic fallback: extract symbol-ish + condition + threshold from free text
    and resolve the symbol via resolve_symbol(). Returns normalized dict or None.
    """
    txt = (prompt or "").strip()

    # candidate symbol or name
    cand_sym = _extract_symbolish(txt) or txt
    symbol = resolve_symbol(cand_sym)
    if not symbol:
        return None

    # condition
    cond: Optional[str] = None
    up = txt.upper()
    if re.search(r"\b(MAYOR|SUPERA|ARRIBA|>\s*=?)\b", up) or re.search(
        r"\b(ABOVE|GREATER|OVER)\b", up
    ):
        cond = "mayor"
    elif re.search(r"\b(MENOR|BAJA|CAE|DEBAJO|<\s*=?)\b", up) or re.search(
        r"\b(BELOW|LESS|UNDER)\b", up
    ):
        cond = "menor"

    # threshold
    m_num = re.search(r"(\d+(?:[.,]\d+)?)", txt)
    threshold = float(m_num.group(1).replace(",", ".")) if m_num else None

    if symbol and cond and threshold is not None:
        return {"simbolo": symbol, "condicion": cond, "umbral": threshold}
    return None


# ------------------------------------------------------------------------------
# Alert creation (LLM JSON mold + resolve_symbol + fallback)
# ------------------------------------------------------------------------------
async def crear_alerta_from_llm(prompt: str, db: Session):
    """
    1) Ask LLM for the strict JSON mold: {"simbolo","condicion","umbral"} (no extra text).
    2) Normalize values; resolve the symbol with resolve_symbol(simbolo) or resolve_symbol(prompt).
    3) If LLM fails, use _regex_fallback(prompt).
    """
    molde = '{"simbolo":"<TICKER|NOMBRE>","condicion":"mayor|menor|auto","umbral":123.45}'
    instr = (
        "Devuelve SOLO un JSON (sin texto extra) con estas claves EXACTAS:\n"
        + molde +
        "\n- Si el usuario dice 'sube', 'mayor', 'supera' -> 'mayor'\n"
        "- Si el usuario dice 'baja', 'menor', 'cae' -> 'menor'\n"
        "- Si NO especifica dirección (ej: 'alerta amd 200') -> 'auto'\n"
        "No expliques nada. Solo el JSON.\n"
        f"Solicitud: '{prompt}'"
    )

    raw = await ask_llm(instr)

    payload = None
    json_err = None
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("JSON no es objeto")

        # tolerate english keys too
        simbolo_in = (
            data.get("simbolo") or data.get("symbol") or data.get("ticker") or ""
        ).strip()
        condicion_in = (
            (data.get("condicion") or data.get("condition") or "").strip().lower()
        )
        umbral_in = (
            data.get("umbral")
            if data.get("umbral") is not None
            else data.get("threshold")
        )

        # resolve symbol (same engine as financial flow)
        symbol = resolve_symbol(simbolo_in) or resolve_symbol(prompt)

        # normalize threshold
        if isinstance(umbral_in, (int, float)):
            umbral = float(umbral_in)
        else:
            s = str(umbral_in or "").replace(",", ".")
            mnum = re.search(r"(\d+(?:\.\d+)?)", s)
            umbral = float(mnum.group(1)) if mnum else None

        # Smart Direction Logic
        condicion = None
        if condicion_in in {"mayor","arriba","supera","sube",">",">=","gt","ge","above","greater","over"}:
            condicion = "mayor"
        elif condicion_in in {"menor","abajo","debajo","cae","baja","<","<=","lt","le","below","less","under"}:
            condicion = "menor"
        elif condicion_in == "auto" and symbol and umbral is not None:
            # Infer direction from current price
            # If target > current -> we want to know when it goes UP (mayor)
            # If target < current -> we want to know when it goes DOWN (menor)
            snap = get_last_price(symbol)
            if snap and snap.price is not None:
                if umbral > snap.price:
                    condicion = "mayor"
                else:
                    condicion = "menor"
            else:
                # Fallback if no price available: assume mayor? or fail?
                # Let's default to mayor if unknown, or maybe fail.
                # User usually sets targets above current price for stocks?
                # But for "stop loss" logic it's below.
                # Let's default to 'mayor' as a safe bet or keep it None to fail.
                condicion = "mayor" # Fallback

        if not (symbol and condicion and umbral is not None):
            raise ValueError("faltan campos requeridos tras normalizacion/resolucion")

        payload = {"simbolo": symbol, "condicion": condicion, "umbral": umbral}
    except Exception as e:
        json_err = str(e)

    if not payload:
        payload = _regex_fallback(prompt)

    if not payload:
        return {"error": f"No se pudo procesar la alerta: {json_err}", "raw": raw}

    try:
        alerta = Alerta(
            simbolo=payload["simbolo"],
            condicion=payload["condicion"],
            umbral=float(payload["umbral"]),
        )
        db.add(alerta)
        db.commit()
        db.refresh(alerta)
        return {
            "mensaje": "✅ Alerta creada",
            "alerta": {
                "id": alerta.id,
                "simbolo": alerta.simbolo,
                "condicion": alerta.condicion,
                "umbral": alerta.umbral,
            },
        }
    except Exception as e:
        return {"error": f"No se pudo guardar la alerta: {e}", "data": payload}


# ------------------------------------------------------------------------------
# Financial quote from free-text prompt (resolve_symbol + market)
# ------------------------------------------------------------------------------
async def quote_from_prompt(prompt: str) -> Dict[str, Any]:
    """
    Resolve a symbol from the user text (no LLM if possible),
    otherwise ask LLM for a pure ticker (few-shot), sanitize and resolve again.
    Then return price + 1h/24h/7d changes.
    """
    # 1) Try resolving directly from the user prompt
    ticker = resolve_symbol(prompt)

    # 2) If unknown, ask LLM with strict examples; then sanitize & resolve again.
    if not ticker:
        llm_hint = await ask_llm(
            "Devuelve SOLO el ticker en mayusculas, sin texto extra.\n"
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
        return {
            "error": "No pude resolver el simbolo. Prueba con el ticker (ej. MSFT) o el nombre exacto."
        }

    if not is_liquid_symbol(ticker):
        return {"error": f"{ticker} parece OTC/iliquido. Usa un ticker regular."}

    try:
        snap = get_last_price(ticker)
    except Exception as e:
        msg = str(e)
        if "Rate limit" in msg or "Too Many Requests" in msg:
            return {
                "error": "Proveedor de precios rate limitado. Intenta de nuevo en unos minutos."
            }
        return {"error": f"No se pudo obtener el precio de {ticker}: {msg}"}

    if snap.price is None:
        return {"error": f"No se pudo obtener el precio de {ticker}"}

    try:
        chg1h, chg24h, chg7d = get_changes(ticker)
    except Exception:
        chg1h, chg24h, chg7d = (None, None, None)
    return {
        "respuesta": f"Precio {snap.name} ({snap.symbol}): {round(snap.price, 2)} USD",
        "cambios": {"1h": chg1h, "24h": chg24h, "7d": chg7d},
        "mercado_abierto": is_market_open(ticker),
    }
