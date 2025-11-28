import pytest


@pytest.mark.asyncio
async def test_intent_financiero_adapter(monkeypatch):
    monkeypatch.setenv('INTENT_MODE', 'ADAPTER')
    from app.api.services import classify_intent
    y = await classify_intent('precio de tsla')
    assert y == 1


@pytest.mark.asyncio
async def test_intent_alerta_adapter(monkeypatch):
    monkeypatch.setenv('INTENT_MODE', 'ADAPTER')
    from app.api.services import classify_intent
    y = await classify_intent('avisame si TSLA cae de 300')
    assert y == 2


@pytest.mark.asyncio
async def test_intent_general_adapter(monkeypatch):
    monkeypatch.setenv('INTENT_MODE', 'ADAPTER')
    from app.api.services import classify_intent
    y = await classify_intent('que es un modelo de lenguaje')
    assert y == 0


@pytest.mark.asyncio
async def test_intent_explain_adapter(monkeypatch):
    monkeypatch.setenv('INTENT_MODE', 'ADAPTER')
    from app.api.services import classify_intent
    y = await classify_intent('que paso con tsla hoy')
    assert y == 3


@pytest.mark.asyncio
async def test_intent_news_adapter(monkeypatch):
    monkeypatch.setenv('INTENT_MODE', 'ADAPTER')
    from app.api.services import classify_intent
    y = await classify_intent('noticias de tsla')
    assert y == 4
