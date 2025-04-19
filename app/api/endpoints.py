from fastapi import APIRouter, HTTPException
from app.api.services import search_google, scrape_website, analizar_con_llm, extraer_contenido_entre_corchetes
from app.core.llm import ask_llm
from fastapi import Body
from app.models.schema import PromptRequest

router = APIRouter()

@router.post("/consulta/")
async def consulta(data: PromptRequest):
    prompt = data.prompt
    pregunta_llm = f"""Reformula esta consulta como la escribirías tú en Google, usando solo palabras clave claras y directas. Devuelve únicamente esa búsqueda sin explicaciones, sin comillas ni corchetes:

    {prompt}"""

    busqueda = (await ask_llm(pregunta_llm)).strip()

    if not busqueda:
        raise HTTPException(status_code=400, detail="El LLM no entregó una búsqueda válida.")
    urls = await search_google(busqueda[0])

    contenidos = {}
    for url in urls:
        contenido = await scrape_website(url)
        contenidos[url] = contenido

    respuesta_final = await analizar_con_llm(prompt, contenidos, ask_llm)

    return {
        "busqueda_generada": busqueda[0],
        "urls": urls,
        "respuesta": respuesta_final
    }
