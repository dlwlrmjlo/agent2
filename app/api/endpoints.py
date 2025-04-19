from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.schema import PromptRequest
from app.api.services import analizar_web
from app.api.services import crear_alerta_from_llm
from app.core.llm import ask_llm
from app.db.database import SessionLocal
import yfinance as yf
import re

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/consulta")
async def consulta(data: PromptRequest, db: Session = Depends(get_db)):
    prompt = data.prompt.strip()

    # Clasificación con 3 opciones
    pregunta = f"""Clasifica la siguiente consulta como:
- 'financiero' si es sobre acciones o criptomonedas,
- 'general' si no lo es,
- o 'alerta' si el usuario quiere configurar una condición o notificación.

Consulta: \"{prompt}\"
Responde solo con una palabra: financiero, general o alerta."""
    tipo = await ask_llm(pregunta)
    tipo = tipo.lower().strip()

    if tipo == "financiero":
        ticker_raw = await ask_llm(
            f"Dime el ticker del activo mencionado en: '{prompt}'. Responde únicamente con el símbolo sin explicar nada más."
        )
        print("🧠 Ticker crudo del LLM:", ticker_raw)

        match = re.search(r"\b[A-Z]{2,5}\b", ticker_raw.upper())
        if match:
            ticker = match.group(0)
        else:
            return {"error": f"No se pudo extraer un símbolo válido desde: '{ticker_raw}'"}

        try:
            data = yf.Ticker(ticker)
            precio = data.info.get("regularMarketPrice", "Precio no disponible")
            nombre = data.info.get("shortName", ticker)
            return {"respuesta": f"El precio actual de {nombre} ({ticker}) es: {precio} USD"}
        except Exception as e:
            return {"error": f"No se pudo obtener el precio del activo: {str(e)}"}

    elif tipo == "alerta":
        return await crear_alerta_from_llm(prompt, db)

    else:
        resultado = await analizar_web(prompt)
        return {"respuesta": resultado}

@router.get("/debug/alertas")
def listar_alertas(db: Session = Depends(get_db)):
    from app.db.models import Alerta
    alertas = db.query(Alerta).all()
    return [{"simbolo": a.simbolo, "condicion": a.condicion, "umbral": a.umbral, "notificado": a.notificado} for a in alertas]

