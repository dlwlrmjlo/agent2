# app/api/services.py
import json, re, httpx
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
from app.core.llm import ask_llm
from app.db.models import Alerta
from app.core.symbols import resolve_symbol  # 👈 usar el mismo resolver

# ---------------------------------------------------------------------------
# web utils (sin cambios)
async def search_google(query: str, num_results: int = 3):
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
    busqueda = reformulado.strip()
    urls = await search_google(busqueda)
    contenidos = {u: await scrape_website(u) for u in urls}
    resumen = "\n\n".join([f"{u}:\n{t[:800]}" for u, t in contenidos.items()])
    prompt_final = f"""La consulta fue: {prompt}

Fuentes encontradas:

{resumen}

Redacta una respuesta clara y útil."""
    return await ask_llm(prompt_final)

# ---------------------------------------------------------------------------
# Alert helpers (limpios, sin aliases hardcodeados)

def _extract_symbolish(text: str) -> str | None:
    """Toma el primer token con pinta de símbolo."""
    if not text:
        return None
    m = re.search(r"\b[A-Z0-9.\-]{2,12}\b", text.upper())
    return m.group(0) if m else None

def _regex_fallback(prompt: str):
    """
    Fallback determinista: intenta extraer datos sueltos desde el prompt
    y resolver el símbolo con resolve_symbol(). Si no se puede, devuelve None.
    """
    txt = (prompt or "").strip()
    # candidato de símbolo (puede ser nombre o ticker)
    cand_sym = _extract_symbolish(txt) or txt
    symbol = resolve_symbol(cand_sym)
    if not symbol:
        return None

    # condición
    cond = None
    up   = txt.upper()
    if re.search(r"\b(MAYOR|SUPERA|ARRIBA|>\s*=?)\b", up):
        cond = "mayor"
    elif re.search(r"\b(MENOR|BAJA|CAE|DEBAJO|<\s*=?)\b", up):
        cond = "menor"
    else:
        # también español “suba/baje” o inglés “above/below”
        if re.search(r"\b(ABOVE|GREATER|OVER)\b", up): cond = "mayor"
        if re.search(r"\b(BELOW|LESS|UNDER)\b", up):   cond = "menor"

    # umbral
    m_num = re.search(r"(\d+(?:[.,]\d+)?)", txt)
    threshold = float(m_num.group(1).replace(",", ".")) if m_num else None

    if symbol and cond and threshold is not None:
        return {"simbolo": symbol, "condicion": cond, "umbral": threshold}
    return None

# ---------------------------------------------------------------------------
# Crear alerta con molde + resolver de símbolos

async def crear_alerta_from_llm(prompt: str, db: Session):
    """
    1) Pedimos SOLO el molde JSON {simbolo, condicion, umbral}.
    2) Normalizamos y resolvemos el símbolo con resolve_symbol() usando:
       - el valor devuelto por el LLM
       - y en fallback, el prompt completo.
    3) Si el LLM no sirve, usamos _regex_fallback(prompt).
    """
    molde = '{"simbolo":"<TICKER|NOMBRE>","condicion":"mayor|menor","umbral":123.45}'
    instr = (
        "Devuelve SOLO un JSON (sin texto extra) con estas claves EXACTAS:\n"
        + molde +
        "\nNo expliques nada. Solo el JSON.\n"
        f"Solicitud: '{prompt}'"
    )

    raw = await ask_llm(instr)

    payload = None
    json_err = None
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("JSON no es objeto")

        # leer campos tolerando ruido
        simbolo_in   = (data.get("simbolo") or data.get("symbol") or data.get("ticker") or "").strip()
        condicion_in = (data.get("condicion") or data.get("condition") or "").strip().lower()
        umbral_in    = data.get("umbral") if data.get("umbral") is not None else data.get("threshold")

        # normalizar condicion
        if condicion_in in {"mayor","arriba","supera","sube",">",">=","gt","ge","above","greater","over"}:
            condicion = "mayor"
        elif condicion_in in {"menor","abajo","debajo","cae","baja","<","<=","lt","le","below","less","under"}:
            condicion = "menor"
        else:
            condicion = None

        # normalizar umbral
        if isinstance(umbral_in, (int, float)):
            umbral = float(umbral_in)
        else:
            s = str(umbral_in or "").replace(",", ".")
            m = re.search(r"(\d+(?:\.\d+)?)", s)
            umbral = float(m.group(1)) if m else None

        # 🔑 resolver símbolo con el mismo motor que usas para /consulta
        # intentamos en este orden: simbolo del LLM → prompt completo
        symbol = resolve_symbol(simbolo_in) or resolve_symbol(prompt)

        if not (symbol and condicion and umbral is not None):
            raise ValueError("faltan campos requeridos tras normalización/resolución")

        payload = {"simbolo": symbol, "condicion": condicion, "umbral": umbral}
    except Exception as e:
        json_err = str(e)

    if not payload:
        # Fallback determinista completamente local
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
