# tests/test_market.py
import pytest
import pandas as pd
from datetime import datetime, timezone, timedelta

def _df_1m():
    # Serie 1m simple: Close = [100, 105, 110]
    now = datetime.now(timezone.utc)  # aware
    idx = pd.date_range(end=now, periods=3, freq="1min", tz="UTC")
    return pd.DataFrame({"Close": [100.0, 105.0, 110.0]}, index=idx)

def _df_5m():
    # Serie 5m simple para deltas: Close = [100, 120] (sube 20%)
    now = datetime.utcnow()
    idx = pd.date_range(end=now, periods=2, freq="5min")
    return pd.DataFrame({"Close": [100.0, 120.0]}, index=idx)

class _FakeTickerWithLastPrice:
    def __init__(self, last_price: float, calls: dict):
        self.fast_info = {"lastPrice": last_price, "shortName": "Fake Inc"}
        self.info = {"shortName": "Fake Inc"}
        self._calls = calls

    def history(self, period: str, interval: str):
        # Si el core usa fast_info correctamente, no debería llamarse.
        self._calls["count"] = self._calls.get("count", 0) + 1
        # Devuelve algo por si acaso (no debería usarse en este test)
        if interval == "1m":
            return _df_1m()
        return _df_5m()

class _FakeTickerNoLastPrice:
    def __init__(self, calls: dict):
        self.fast_info = {"lastPrice": None, "shortName": "NoFast"}
        self.info = {"shortName": "NoFast"}
        self._calls = calls

    def history(self, period: str, interval: str):
        self._calls["count"] = self._calls.get("count", 0) + 1
        if interval == "1m":
            return _df_1m()
        return _df_5m()

class _FakeYFWithLastPrice:
    def __init__(self, last_price: float, calls: dict):
        self._last = last_price
        self._calls = calls
    def Ticker(self, symbol: str):
        return _FakeTickerWithLastPrice(self._last, self._calls)

class _FakeYFNoLastPrice:
    def __init__(self, calls: dict):
        self._calls = calls
    def Ticker(self, symbol: str):
        return _FakeTickerNoLastPrice(self._calls)

def _fake_yf_with_lastprice(last_price: float):
    calls = {"count": 0}
    return _FakeYFWithLastPrice(last_price, calls), calls

def _fake_yf_without_lastprice(calls: dict):
    return _FakeYFNoLastPrice(calls)


def test_fast_info_preferred(monkeypatch):
    """
    Si fast_info.lastPrice existe, get_last_price debe usarlo
    y NO llamar a history(). Verificamos count == 0 tras la llamada.
    """
    from app.core import market
    fake_yf, calls = _fake_yf_with_lastprice(200.0)
    monkeypatch.setattr(market, "yf", fake_yf, raising=False)

    snap = market.get_last_price("MSFT")
    assert snap.price == 200.0
    assert calls["count"] == 0, "Con lastPrice, no debería invocar history()"

def test_fallback_to_history_when_no_lastprice(monkeypatch):
    """
    Cuando no hay lastPrice, get_last_price debe caer a history(1m) y
    devolver el último close (=110.0 en nuestro DF sintético).
    """
    from app.core import market
    calls = {"count": 0}
    fake_yf = _fake_yf_without_lastprice(calls)
    monkeypatch.setattr(market, "yf", fake_yf, raising=False)

    snap = market.get_last_price("AAPL")
    assert snap.price == 110.0, f"Se esperaba 110.0 desde 1m history, got {snap.price}"
    assert calls["count"] >= 1, "Debió llamar al menos una vez a history() para 1m"

def test_cache_ttl_no_extra_history_on_second_call(monkeypatch):
    """
    1ª pasada:
      - Puede haber 1 o 2 llamadas a history() según el diseño del cache:
        * Si cachea por símbolo (tu caso actual): 1 llamada (usa 1m y reutiliza para get_changes)
        * Si cachea por intervalo: 2 llamadas (1m para precio, 5m para deltas)
    2ª pasada inmediata:
      - No debe aumentar el contador (reutiliza cache).
    """
    from app.core import market
    calls = {"count": 0}
    fake_yf = _fake_yf_without_lastprice(calls)
    monkeypatch.setattr(market, "yf", fake_yf, raising=False)

    # 1ª pasada
    _ = market.get_last_price("TSLA")
    _ = market.get_changes("TSLA")
    first = calls["count"]
    assert first >= 1, f"Esperaba al menos 1 llamada en la 1ª pasada, got {first}"

    # 2ª pasada (caches calientes)
    _ = market.get_last_price("TSLA")
    _ = market.get_changes("TSLA")
    second = calls["count"]

    assert second == first, "Debe reutilizar cache y no volver a llamar history() en la 2ª pasada"
