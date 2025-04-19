from fastapi import APIRouter
from app.models.schema import PromptRequest
from app.api.services import analizar_web
from app.core.llm import ask_llm
import yfinance as yf
import re

router = APIRouter()


@router.post("/consulta")
async def consulta(data: PromptRequest):
    prompt = data.prompt.strip()

    # Clasificación del tipo de pregunta
    pregunta = f"""Clasifica la siguiente consulta como 'financiero' si es sobre acciones o criptomonedas, 
    'tarea' si es que la consulta contiene la palabra tarea en alguna parte o 'general' si no es ninguna de las dos: \"{prompt}\". Devuelve solo una palabra."""
    tipo = await ask_llm(pregunta)
    tipo = tipo.lower().strip()

    if tipo == "financiero":
        # Extraer ticker desde LLM
        ticker_raw = await ask_llm(
            f"Dime el ticker del activo mencionado en: '{prompt}'. Responde únicamente con el símbolo, sin texto adicional."
        )
        print("🧠 Ticker crudo del LLM:", ticker_raw)

        # Extraer símbolo con regex
        match = re.search(r"\b[A-Z]{2,5}\b", ticker_raw.upper())
        if match:
            ticker = match.group(0)
        else:
            return {"error": f"No se pudo extraer un símbolo válido desde: '{ticker_raw}'"}
        print("ticker extraido:", ticker)

        # Obtener precio desde yfinance
        try:
            data = yf.Ticker(ticker)
            precio = data.info.get("regularMarketPrice", "Precio no disponible")
            nombre = data.info.get("shortName", ticker)
            return {"respuesta": f"El precio actual de {nombre} ({ticker}) es: {precio} USD"}
        except Exception as e:
            return {"error": f"No se pudo obtener el precio del activo: {str(e)}"}

    else:
        # Scraping general
        resultado = await analizar_web(prompt)
        return {"respuesta": resultado}
