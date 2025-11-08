# tests/test_symbols.py
import pytest

def _get_resolver(symbols_module):
    """
    Soporta distintos nombres por si tu módulo expone otra firma:
    resolve_symbol | resolve | resolve_ticker
    """
    for name in ("resolve_symbol", "resolve", "resolve_ticker"):
        fn = getattr(symbols_module, name, None)
        if callable(fn):
            return fn
    raise AttributeError("No resolver found in app.core.symbols")

def _extract_sym(result):
    """
    Normaliza el output para comparar: string | dict['symbol'] | obj.symbol
    """
    if result is None:
        return None
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        return result.get("symbol") or result.get("ticker") or result.get("Symbol")
    return getattr(result, "symbol", None) or getattr(result, "ticker", None)

def test_direct_ticker_returns_same(monkeypatch):
    """
    Input 'TSLA' debe resolverse a 'TSLA' sin depender de búsquedas.
    Mockeamos yfinance para que, si el resolver valida el ticker,
    encuentre datos mínimos y no falle.
    """
    import app.core.symbols as symbols

    class _FakeTicker:
        def __init__(self, sym):
            self.sym = sym
            # Mínimos por si el resolver mira estos campos
            self.fast_info = {"shortName": "Tesla, Inc.", "lastPrice": 250.0}
            self.info = {"shortName": "Tesla, Inc."}
        # Si tu resolver llega a consultar history(), devolvemos un stub con .empty
        def history(self, *args, **kwargs):
            class _DF:
                empty = True
            return _DF()

    class _FakeYF:
        def Ticker(self, sym):
            return _FakeTicker(sym)
        # Si tu resolver hace algún search, que no explote:
        def __getattr__(self, name):
            # fallback para cualquier otra cosa que no usemos
            raise AttributeError(name)

    # Forzamos que “parece ticker” siempre sea True para TSLA si existe esa heurística
    if hasattr(symbols, "_looks_like_ticker"):
        monkeypatch.setattr(symbols, "_looks_like_ticker", lambda s: True)

    # Inyectamos nuestro yfinance falso
    monkeypatch.setattr(symbols, "yf", _FakeYF(), raising=False)

    resolver = _get_resolver(symbols)
    out = resolver("TSLA")
    assert _extract_sym(out) == "TSLA"
