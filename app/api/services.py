# app/api/services.py
from googlesearch import search
from bs4 import BeautifulSoup
import httpx
from app.core.llm import ask_llm
import json
from sqlalchemy.orm import Session
from app.core.llm import ask_llm
from app.db.models import Alerta

async def search_google(query: str, num_results: int = 3):
    return list(search(query, num_results=num_results))

async def scrape_website(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
    except Exception as e:
        return f"[ERROR scraping {url}]: {str(e)}"

    soup = BeautifulSoup(response.text, "lxml")
    return " ".join(p.get_text() for p in soup.find_all("p"))[:4000]

async def analizar_web(prompt: str) -> str:
    reformulado = await ask_llm(f"Reformula esta búsqueda para Google: {prompt}")
    busqueda = reformulado.strip()
    urls = await search_google(busqueda)

    contenidos = {}
    for url in urls:
        contenidos[url] = await scrape_website(url)

    resumen = "\n\n".join([f"{url}:\n{texto[:800]}" for url, texto in contenidos.items()])
    prompt_final = f"""La consulta fue: {prompt}

Fuentes encontradas:

{resumen}

Redacta una respuesta clara y útil."""
    return await ask_llm(prompt_final)

async def crear_alerta_from_llm(prompt: str, db: Session):
    # Pedimos al LLM que genere una alerta estructurada como JSON
    instrucciones = f"""
Estructura la siguiente solicitud como una alerta de precio en formato JSON con estas claves:
- 'simbolo': el ticker o símbolo del activo
- 'condicion': puede ser 'mayor' o 'menor'
- 'umbral': el valor numérico umbral

Ejemplo de salida esperada:
{{ "simbolo": "BTC", "condicion": "menor", "umbral": 30000 }}

Solicitud del usuario: '{prompt}'
"""

    respuesta = await ask_llm(instrucciones)
    print("🧠 LLM alerta JSON:", respuesta)

    try:
        data = json.loads(respuesta)
        alerta = Alerta(
            simbolo=data["simbolo"].strip().upper(),
            condicion=data["condicion"].strip().lower(),
            umbral=float(data["umbral"])
        )
        db.add(alerta)
        db.commit()
        db.refresh(alerta)
        return {"mensaje": "✅ Alerta creada exitosamente", "alerta": {
            "simbolo": alerta.simbolo,
            "condicion": alerta.condicion,
            "umbral": alerta.umbral
        }}
    except Exception as e:
        return {"error": f"No se pudo procesar la alerta: {str(e)}"}
