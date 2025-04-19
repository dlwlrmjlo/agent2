from googlesearch import search
from bs4 import BeautifulSoup
import httpx
import re

async def search_google(query: str, num_results: int = 3):
    return list(search(query, num_results=num_results))

async def scrape_website(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        text = " ".join(p.get_text() for p in soup.find_all("p"))
        return text[:4000]
    except Exception as e:
        return f"[Error scraping {url}]: {str(e)}"

async def analizar_con_llm(query: str, contenidos: dict, ask_llm_fn) -> str:
    resumen = ""
    for url, contenido in contenidos.items():
        resumen += f"\nFuente: {url}\n{contenido[:1000]}\n"

    prompt = f"""
Eres un asistente de inteligencia artificial. El usuario preguntó:

"{query}"

Estos son los resultados que encontramos en la web:

{resumen}

Redacta una respuesta clara, útil y resumida.
    """
    return await ask_llm_fn(prompt)

