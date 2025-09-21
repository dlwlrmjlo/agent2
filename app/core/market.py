# app/core/market.py
# Fast, safe price access with micro TTL cache and fallbacks.

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import time, threading
import yfinance as yf

class _TTLCache:
    def __init__(self, ttl_s=15, maxsize=512):
        self.ttl = ttl_s; self.maxsize = maxsize
        self._data = {}; self._lock = threading.RLock()
    def get(self, k):
        with self._lock:
            v = self._data.get(k)
            if not v: return None
            val, ts = v
            if time.time() - ts > self.ttl:
                self._data.pop(k, None); return None
            return val
    def set(self, k, val):
        with self._lock:
            if len(self._data) >= self.maxsize: self._data.clear()
            self._data[k] = (val, time.time())

_price = _TTLCache(15); _hist = _TTLCache(60)

@dataclass
class PriceSnapshot:
    symbol: str
    name: str
    price: Optional[float]
    ts: float

def _norm(sym: str) -> str:
    s = (sym or "").upper().strip()
    return "BTC-USD" if s == "BTC" else s

def get_last_price(symbol: str) -> PriceSnapshot:
    """Use fast_info when possible; fallback to last 1m close."""
    symbol = _norm(symbol)
    c = _price.get(symbol)
    if c: return c
    t = yf.Ticker(symbol)
    name = t.fast_info.get("shortName") or t.info.get("shortName") or symbol
    price = t.fast_info.get("lastPrice")
    if price is None:
        h = _hist.get(symbol)
        if h is None:
            h = t.history(period="1d", interval="1m")
            _hist.set(symbol, h)
        if not h.empty:
            price = float(h["Close"].iloc[-1])
    snap = PriceSnapshot(symbol=symbol, name=name, price=(float(price) if price is not None else None), ts=time.time())
    _price.set(symbol, snap)
    return snap

def get_changes(symbol: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """(%1h,%24h,%7d) from a 7d/5m history window."""
    symbol = _norm(symbol)
    h = _hist.get(symbol)
    if h is None:
        t = yf.Ticker(symbol)
        h = t.history(period="7d", interval="5m")
        _hist.set(symbol, h)
    if h is None or h.empty: return (None, None, None)

    def pct(minutes: int):
        n = max(1, int(minutes / 5))
        w = h.tail(n)
        if w.empty: return None
        a, b = float(w["Close"].iloc[0]), float(w["Close"].iloc[-1])
        if a == 0.0: return None
        return (b - a) * 100.0 / a

    return (pct(60), pct(24*60), pct(7*24*60))
