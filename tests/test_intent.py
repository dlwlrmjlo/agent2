# tests/test_intent.py
import os
import pytest

@pytest.mark.asyncio
async def test_intent_financiero_adapter(monkeypatch):
    # Forzar modo ADAPTER
    monkeypatch.setenv("INTENT_MODE", "ADAPTER")

    from app.api.services import classify_intent  # import con env listo
    y = await classify_intent("precio de tesla")
    assert y == 1  # financiero

@pytest.mark.asyncio
async def test_intent_alerta_adapter(monkeypatch):
    monkeypatch.setenv("INTENT_MODE", "ADAPTER")
    from app.api.services import classify_intent
    y = await classify_intent("avísame si TSLA cae de 300")
    assert y == 2  # alerta

@pytest.mark.asyncio
async def test_intent_general_adapter(monkeypatch):
    monkeypatch.setenv("INTENT_MODE", "ADAPTER")
    from app.api.services import classify_intent
    y = await classify_intent("qué pasó con SQM")
    assert y == 0  # general

@pytest.fixture()
def mock_yfinance(monkeypatch):
    """
    Fake yfinance.Ticker with:
      - fast_info.lastPrice (configurable por test)
      - history(interval="1m"|"1h"|"1d") devolviendo DataFrame determinista
    Además cuenta cuántas veces se llama `history` para testear cache/fallback.
    """
    calls = {"history": 0}

    class _FastInfo:
        def __init__(self, last_price):
            self.lastPrice = last_price

    class _FakeTicker:
        def __init__(self, symbol, last_price=123.45):
            self.symbol = symbol
            self.fast_info = _FastInfo(last_price)

        def history(self, period="7d", interval="1m"):
            calls["history"] += 1
            now = dt.datetime.now()
            # Generamos serie sintética con tendencias simples para verificar deltas.
            if interval == "1m":
                idx = pd.date_range(end=now, periods=10, freq="1min")
                base = 100.0
                # última vela = 110 (sube 10% desde 100)
                closes = np.linspace(base, 110.0, len(idx))
            elif interval == "1h":
                idx = pd.date_range(end=now, periods=10, freq="1h")
                base = 90.0
                # última vela = 99 (sube 10% desde 90)
                closes = np.linspace(base, 99.0, len(idx))
            else:  # "1d"
                idx = pd.date_range(end=now, periods=10, freq="1d")
                base = 80.0
                # última vela = 88 (sube 10% desde 80)
                closes = np.linspace(base, 88.0, len(idx))

            df = pd.DataFrame({"Close": closes}, index=idx)
            return df

    def _fake_Ticker(sym):
        # lastPrice por defecto; los tests lo ajustan si quieren forzar fallback
        return _FakeTicker(sym)

    # monkeypatch del módulo yfinance usado por app.core.market
    import builtins
    try:
        import app.core.market  # asegura que existe antes de parchear
    except Exception:
        pass

    import types as _types
    yfinance_stub = _types.SimpleNamespace(Ticker=_fake_Ticker)
    monkeypatch.setitem(globals(), "calls_market_history", calls)  # opcional si necesitas fuera
    monkeypatch.setattr("app.core.market.yf", yfinance_stub, raising=False)

    # Exponemos controles al test
    return {"calls": calls, "factory": _FakeTicker}
