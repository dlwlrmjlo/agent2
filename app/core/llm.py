# app/core/llm.py
# Thin async client for Ollama (non-stream)

import httpx
from app.core.config import settings

async def ask_llm(prompt: str) -> str:
    """Call Ollama with a plain prompt and return the 'response' field."""
    payload = {"model": settings.MODEL_NAME, "prompt": prompt, "stream": False}
    headers = {"Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=settings.TIMEOUT) as client:
        r = await client.post(settings.OLLAMA_API, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
        out = data.get("response", "").strip()
        print("🧠 LLM PROMPT:\n", prompt, "\n🗣️ RESPUESTA:\n", out, "\n", "-" * 80)
        return out or "[Sin respuesta]"
