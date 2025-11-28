# app/api/services.py
# All application services in one place:
# - Web analysis (LLM + light scraping)
# - Intent classification (heuristics + LLM → 0/1/2)
# - Alert creation (LLM strict mold + resolve_symbol + regex fallback)
# - Financial quote from prompt (resolve_symbol + market)

from __future__ import annotations

import json, re, httpx
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.llm import ask_llm
from app.core.intent_adapter import predict as adapter_predict
from app.core.symbols import resolve_symbol
from app.core.market import get_last_price, get_changes
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
    reformulado = await ask_llm(f"Reformula esta búsqueda para Google: {prompt}")
    busqueda = (reformulado or "").strip() or prompt
    urls = await search_google(busqueda)
    contenidos = {u: await scrape_website(u) for u in urls}
    resumen = "\n\n".join([f"{u}:\n{t[:800]}" for u, t in contenidos.items()])
    prompt_final = f"""La consulta fue: {prompt}

Fuentes encontradas:

{resumen}

Redacta una respuesta clara y útil."""
    return await ask_llm(prompt_final)


# ------------------------------------------------------------------------------
# Intent classification (0=GENERAL, 1=FINANCIERO, 2=ALERTA)
# ------------------------------------------------------------------------------
def _looks_like_alert(text: str) -> bool:
    t = (text or "").lower()
    if re.search(r"\b(alerta|alertame|av[íi]same|avisame|notifica|notificar)\b", t):
        return True
    return bool(re.search(r"\b(si|cuando)\b.*\b(sube|baja|supera|cae|rompe|cruza)\b.*\d", t))

def _looks_like_financial(text: str) -> bool:
    t = (text or "").lower()
    if re.search(r"\b(precio|cotiza|cotizaci[óo]n|quote|price|valor)\b", t):
        return True
    return bool(re.search(r"\b[A-Z0-9.\-]{2,12}\b", (text or "").upper()))

async def classify_intent(text: str) -> int:
    t = (text or "").strip()
    mode = (settings.INTENT_MODE or "HYBRID").upper()

    if mode == "ADAPTER":
        y, _ = adapter_predict(t)
        return int(y)

    if mode == "LLM":
        prompt = (
            "Clasifica la consulta en UNA sola categoría y devuelve SOLO un dígito:\n"
            "0 = general (explicaciones, contexto, noticias)\n"
            "1 = financiero (precio/cotización/quote)\n"
            "2 = alerta (regla con umbral: si/cuando sube/baja de X)\n\n"
            "- \"precio de tesla\" -> 1\n- \"avísame si TSLA cae de 300\" -> 2\n- \"qué pasó con SQM\" -> 0\n\n"
            f"Consulta: \"{t}\"\nResponde SOLO con 0 o 1 o 2."
        )
        raw = (await ask_llm(prompt)) or ""
        m = re.search(r"[0-2]", raw)
        return int(m.group(0)) if m else 0

    # HYBRID (default): adapter rápido y LLM solo si hay duda
    y, p = adapter_predict(t)
    if p >= 0.80:
        return int(y)

    prompt = (
        "Clasifica la consulta en UNA sola categoría y devuelve SOLO un dígito:\n"
        "0 = general\n1 = financiero\n2 = alerta\n\n"
        "- \"precio de tesla\" -> 1\n- \"avísame si TSLA cae de 300\" -> 2\n- \"qué pasó con SQM\" -> 0\n\n"
        f"Consulta: \"{t}\"\nResponde SOLO con 0 o 1 o 2."
    )
    raw = (await ask_llm(prompt)) or ""
    m = re.search(r"[0-2]", raw)
    return int(m.group(0)) if m else int(y)

# ------------------------------------------------------------------------------
# Sub-intent classification for GENERAL (EXPLAIN vs NEWS)
# ------------------------------------------------------------------------------
def _looks_like_news(text: str) -> bool:
    t = (text or "").lower()
    return bool(re.search(r"\b(noticia(s)?|titulares|headlines?|últimas|que se dijo|rss|prensa|news)\b", t))

def _looks_like_explain(text: str) -> bool:
    t = (text or "").lower()
    patterns = [
        r"\bpor que\b", r"\bpor qué\b", r"\bexplica(me)?\b", r"\bdrivers?\b",
        r"\brazones?\b", r"\bmotivo(s)?\b", r"\bcaus(a|as)\b",
        r"\bque paso\b", r"\bqué pasó\b", r"\bwhy\b", r"\bexplain\b"
    ]
    if any(re.search(p, t) for p in patterns):
        return True
    if re.search(r"\b(subi[oó]|baj[oó]|cay[oó]|salt[oó]|rally|sell[\s-]?off)\b", t) and re.search(r"\b(por que|por qué|que paso|qué pasó|why)\b", t):
        return True
    return False

async def classify_general_subintent(text: str) -> str:
    """Return 'NEWS' | 'EXPLAIN' | 'GENERAL' for non-price/alert queries."""
    if _looks_like_explain(text):
        return "EXPLAIN"
    if _looks_like_news(text):
        return "NEWS"

    prompt = (
        "La consulta no es de precios ni alertas. "
        "Clasifica en UNA: news | explain | general.\n"
        "- news: pide titulares/noticias de un ticker.\n"
        "- explain: pide causas (por qué/qué pasó) del movimiento de un ticker.\n"
        "- general: otra cosa.\n\n"
        f"Consulta: \"{(text or '').strip()}\"\n"
        "Responde solo: news | explain | general."
    )
    raw = ((await ask_llm(prompt)) or "").strip().lower()
    if "news" in raw:
        return "NEWS"
    if "explain" in raw:
        return "EXPLAIN"
    return "GENERAL"

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
    "QUE","QUÉ","DE","DEL","LA","EL","LOS","LAS","Y","EN","POR","PARA","CON",
    "AL","UN","UNA","UNOS","UNAS","A","SE","LO","SU","SUS","MI","TUS","SU","NO",
    "SI","CUANDO","SUBE","BAJA","CAI","CAE","ROMPE","CRUZA","HOY","AHORA","CUANTO","PRECIO",
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
        f"Consulta: \"{txt}\"\n"
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
    if re.search(r"\b(MAYOR|SUPERA|ARRIBA|>\s*=?)\b", up) or re.search(r"\b(ABOVE|GREATER|OVER)\b", up):
        cond = "mayor"
    elif re.search(r"\b(MENOR|BAJA|CAE|DEBAJO|<\s*=?)\b", up) or re.search(r"\b(BELOW|LESS|UNDER)\b", up):
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
        simbolo_in   = (data.get("simbolo") or data.get("symbol") or data.get("ticker") or "").strip()
        condicion_in = (data.get("condicion") or data.get("condition") or "").strip().lower()
        umbral_in    = data.get("umbral") if data.get("umbral") is not None else data.get("threshold")

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
            raise ValueError("faltan campos requeridos tras normalización/resolución")

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
        db.add(alerta); db.commit(); db.refresh(alerta)
        return {
            "mensaje": "✅ Alerta creada",
            "alerta": {
                "id": alerta.id,
                "simbolo": alerta.simbolo,
                "condicion": alerta.condicion,
                "umbral": alerta.umbral
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

# ------------------------------------------------------------------------------
# Override: single-step 5-class intent (0=GEN,1=FIN,2=ALERTA,3=EXPLAIN,4=NEWS)
# This redefines classify_intent later in the module to extend labels without
# changing call sites. Adapter will still return 0..2 until retrained.
# ------------------------------------------------------------------------------
async def classify_intent(text: str) -> int:  # type: ignore[no-redef]
    t = (text or "").strip()
    mode = (settings.INTENT_MODE or "HYBRID").upper()

    if mode == "ADAPTER":
        y, _ = adapter_predict(t)
        print("confianza de y en adapter de ", _)
        return int(y)

    if mode == "LLM":
        prompt = (
            "Clasifica la consulta en UNA sola categor��a y devuelve SOLO un d��gito:\n"
            "0 = general (otros; no precio/alerta/explicaci��n/noticias)\n"
            "1 = financiero (precio/cotizaci��n/quote)\n"
            "2 = alerta (regla con umbral: si/cuando sube/baja de X)\n"
            "3 = explain (por qu��/qu�� pas��/drivers de un ticker)\n"
            "4 = news (pide noticias/titulares de un ticker)\n\n"
            "- \"precio de tesla\" -> 1\n"
            "- \"av��same si TSLA cae de 300\" -> 2\n"
            "- \"qu�� pas�� con SQM\" -> 3\n"
            "- \"noticias de AMD\" -> 4\n"
            "- \"contexto de SQM hoy\" -> 0\n\n"
            f"Consulta: \"{t}\"\nResponde SOLO con 0 o 1 o 2 o 3 o 4."
        )
        raw = (await ask_llm(prompt)) or ""
        m = re.search(r"[0-4]", raw)
        return int(m.group(0)) if m else 0

    # HYBRID: adapter primero; si baja confianza, LLM 5-clases
    y, p = adapter_predict(t)
    print("confianza de y en hibrido de ", p)
    if p >= 0.80:
        return int(y)

    prompt = (
        "Clasifica la consulta en UNA sola categor��a y devuelve SOLO un d��gito:\n"
        "0 = general\n1 = financiero\n2 = alerta\n3 = explain\n4 = news\n\n"
        "- \"precio de tesla\" -> 1\n"
        "- \"av��same si TSLA cae de 300\" -> 2\n"
        "- \"qu�� pas�� con SQM\" -> 3\n"
        "- \"noticias de AMD\" -> 4\n"
        "- \"contexto de SQM hoy\" -> 0\n\n"
        f"Consulta: \"{t}\"\nResponde SOLO con 0 o 1 o 2 o 3 o 4."
    )
    raw = (await ask_llm(prompt)) or ""
    m = re.search(r"[0-4]", raw)
    return int(m.group(0)) if m else int(y)
