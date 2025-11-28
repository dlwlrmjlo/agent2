# tests/conftest.py
import os
import sys
from pathlib import Path
import pytest
import logging
import json

# 1) Habilita import "app.*" desde la raíz del repo
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 2) Defaults de entorno para que nada externo moleste en tests
os.environ.setdefault("INTENT_MODE", "ADAPTER")   # forzamos adapter (sin LLM/red)
os.environ.setdefault("DISABLE_SCHEDULER", "1")   # si tu app lo soporta
os.environ.setdefault("ENV", "test")

# 4) Logging detallado en español para cada test (config en pytest.ini)
def pytest_configure(config):
    # Opcional: traducción de nombres de niveles al español
    logging.addLevelName(logging.DEBUG, "DEPURACIÓN")
    logging.addLevelName(logging.WARNING, "ADVERTENCIA")
    logging.addLevelName(logging.ERROR, "ERROR")
    logging.addLevelName(logging.CRITICAL, "CRÍTICO")

# 3) Mock del LLM por si algún test lo llama igual
@pytest.fixture()
def mock_ask_llm(monkeypatch):
    from app.core import llm as llm_mod

    async def _fake(prompt: str) -> str:
        # Respuestas mínimas, deterministas
        if "Clasifica la consulta" in prompt:
            # default: general
            return "0"
        if "Apple" in prompt or "apple" in prompt:
            return "AAPL"
        if "Google" in prompt or "google" in prompt:
            return "GOOGL"
        return "OK"

    monkeypatch.setattr(llm_mod, "ask_llm", _fake)
    
    # Patch also in services.py if it was already imported
    import sys
    if "app.api.services" in sys.modules:
        from app.api import services
        monkeypatch.setattr(services, "ask_llm", _fake)
    
    if "app.core.summarize" in sys.modules:
        from app.core import summarize
        monkeypatch.setattr(summarize, "ask_llm", _fake)
        
    return _fake
 
@pytest.fixture(autouse=True)
def _log_test_start(request):
    logger = logging.getLogger("tests")
    nodeid = request.node.nodeid
    func = getattr(request.node, "function", None)
    doc = (func.__doc__.strip() if func and func.__doc__ else "sin descripción")
    markers = sorted({m.name for m in request.node.iter_markers()})
    marks_str = ", ".join(markers) if markers else "ninguna"
    if hasattr(request.node, "callspec"):
        params = request.node.callspec.params
        try:
            params_str = json.dumps(params, ensure_ascii=False)
        except Exception:
            params_str = str(params)
    else:
        params_str = "ninguno"

    logger.info(
        f"INICIO prueba: {nodeid} — {doc} | Marcas: {marks_str} | Parámetros: {params_str}"
    )
    yield

def pytest_runtest_logreport(report: pytest.TestReport):
    # Loguea solo la fase principal del test (call)
    if report.when != "call":
        return
    logger = logging.getLogger("tests")
    outcome = report.outcome  # 'passed' | 'failed' | 'skipped'
    if outcome == "passed" and getattr(report, "wasxfail", False):
        status = "XPASSED"
    elif outcome == "skipped" and getattr(report, "wasxfail", False):
        status = "XFAILED"
    elif outcome == "passed":
        status = "OK"
    elif outcome == "failed":
        status = "FALLÓ"
    else:
        status = "OMITIDO"

    motivo = None
    try:
        lr = report.longrepr
        if outcome == "skipped":
            if isinstance(lr, tuple) and len(lr) >= 3:
                motivo = str(lr[2])
        elif outcome == "failed":
            if hasattr(lr, "reprcrash") and getattr(lr.reprcrash, "message", None):
                motivo = lr.reprcrash.message
            else:
                motivo = str(lr)
    except Exception:
        motivo = None

    dur_ms = report.duration * 1000.0
    if motivo:
        motivo = (motivo or "").replace("\n", " ")
        if len(motivo) > 300:
            motivo = motivo[:300] + "…"
        logger.info(
            f"FIN prueba: {report.nodeid} -> {status} ({dur_ms:.1f} ms) | Motivo: {motivo}"
        )
    else:
        logger.info(
            f"FIN prueba: {report.nodeid} -> {status} ({dur_ms:.1f} ms)"
        )
