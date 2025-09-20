# app/core/market.py
# Purpose: fast, robust price access with minimal latency and safe fallbacks.
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import time
import threading
import yfinance as yf

# Tiny TTL cache to reduce remote calls and jitter
class _TTLCache:
    def __init__(self, ttl_s: int = 15, maxsize: int = 1024):
        self.ttl = ttl_s
        self.maxsize = maxsize
        self._data = {}
        self._lock = threading.RLock()

    def get(self, key: str):
        with self._lock:
            item = self._data.get(key)
            if not item:
                return None
            value, ts = item
            if time.time() - ts > self.ttl:
                self._data.pop(key, None)
                return None
            return value

    def set(self, key: str, value):
        with self._lock:
            if len(self._data) >= self.maxsize:
                self._data.clear()
            self._data[key] = (value, time.time())

_price_cache = _TTLCache(ttl_s=15)
_hist_cache  = _TTLCache(ttl_s=60)

@dataclass
class PriceSnapshot:
    symbol: str
    name: str
    price: Optional[float]  # None if unavailable
    ts: float               # unix seconds

def _norm_symbol(sym: str) -> str:
    s = (sym or "").upper().strip()
    return "BTC-USD" if s == "BTC" else s

def get_last_price(symbol: str) -> PriceSnapshot:
    """Get last price using fast_info with a safe fallback to history. Cached ~15s."""
    symbol = _norm_symbol(symbol)
    cached = _price_cache.get(symbol)
    if cached:
        return cached

    t = yf.Ticker(symbol)
    name = t.fast_info.get("shortName") or t.info.get("shortName") or symbol
    price = t.fast_info.get("lastPrice", None)

    if price is None:
        # Fallback to the latest minute close if available
        hist = _hist_cache.get(symbol)
        if hist is None:
            hist = t.history(period="1d", interval="1m")
            _hist_cache.set(symbol, hist)
        if not hist.empty:
            price = float(hist["Close"].iloc[-1])

    snap = PriceSnapshot(symbol=symbol, name=name, price=(float(price) if price is not None else None), ts=time.time())
    _price_cache.set(symbol, snap)
    return snap

def get_changes(symbol: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Return (%1h, %24h, %7d) change using history. Cached ~60s via _hist_cache."""
    symbol = _norm_symbol(symbol)
    hist = _hist_cache.get(symbol)
    if hist is None:
        t = yf.Ticker(symbol)
        # We request more data once; slices will be taken from this frame.
        hist = t.history(period="7d", interval="5m")
        _hist_cache.set(symbol, hist)
    if hist is None or hist.empty:
        return (None, None, None)

    # Helper to compute percent change from first to last non-NaN
    def pct_change(minutes: int) -> Optional[float]:
        if hist.empty:
            return None
        # approximate slices
        window = hist.tail(max(1, int(minutes / 5)))  # 5m interval
        if window.empty:
            return None
        first = float(window["Close"].iloc[0])
        last  = float(window["Close"].iloc[-1])
        if first == 0.0:
            return None
        return (last - first) * 100.0 / first

    chg1h  = pct_change(60)
    chg24h = pct_change(24 * 60)
    chg7d  = pct_change(7 * 24 * 60)
    return (chg1h, chg24h, chg7d)
