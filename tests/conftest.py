# tests/conftest.py
import os
import sys
from pathlib import Path
import pytest

# 1) Habilita import "app.*" desde la raíz del repo
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 2) Defaults de entorno para que nada externo moleste en tests
os.environ.setdefault("INTENT_MODE", "ADAPTER")   # forzamos adapter (sin LLM/red)
os.environ.setdefault("DISABLE_SCHEDULER", "1")   # si tu app lo soporta
os.environ.setdefault("ENV", "test")

# 3) Mock del LLM por si algún test lo llama igual
@pytest.fixture()
def mock_ask_llm(monkeypatch):
    from app.core import llm as llm_mod

    async def _fake(prompt: str) -> str:
        # Respuestas mínimas, deterministas
        if "Clasifica la consulta" in prompt:
            # default: general
            return "0"
        return "OK"

    monkeypatch.setattr(llm_mod, "ask_llm", _fake)
    return _fake
