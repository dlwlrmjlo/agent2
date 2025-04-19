import httpx
from app.core.config import settings

async def ask_llm(prompt: str) -> str:
    payload = {
        "model": settings.MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=settings.TIMEOUT) as client:
        response = await client.post(settings.OLLAMA_API, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "[Sin respuesta del modelo]")
