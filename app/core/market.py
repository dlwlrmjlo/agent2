# app/core/market.py
# Fast, safe price access with micro TTL cache and fallbacks.

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Optional, Tuple

import httpx
import yfinance as yf

from app.core.config import settings


class _TTLCache:
    def __init__(self, ttl_s=15, maxsize=512):
        self.ttl = ttl_s
        self.maxsize = maxsize
        self._data = {}
        self._lock = threading.RLock()

    def get(self, k):
        with self._lock:
            v = self._data.get(k)
            if not v:
                return None
            val, ts = v
            if time.time() - ts > self.ttl:
                self._data.pop(k, None)
                return None
            return val

    def set(self, k, val):
        with self._lock:
            if len(self._data) >= self.maxsize:
                self._data.clear()
            self._data[k] = (val, time.time())


_price = _TTLCache(15)
_hist = _TTLCache(60)


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
    """Use fast_info when possible; fallback to last 1m close; then provider fallbacks."""
    symbol = _norm(symbol)
    c = _price.get(symbol)
    if c:
        return c
    price = None
    name = symbol
    try:
        t = yf.Ticker(symbol)
        name = t.fast_info.get("shortName") or t.info.get("shortName") or symbol
        price = t.fast_info.get("lastPrice")
        if price is None:
            h = _hist.get(symbol)
            if h is None:
                h = t.history(period="1d", interval="1m")
                _hist.set(symbol, h)
            if h is not None and not h.empty:
                price = float(h["Close"].iloc[-1])
    except Exception:
        price = None

    # fallbacks
    if price is None:
        snap = _fallback_alpha_vantage(symbol)
        if snap:
            _price.set(symbol, snap)
            return snap
        snap = _fallback_coingecko(symbol)
        if snap:
            _price.set(symbol, snap)
            return snap

    snap = PriceSnapshot(
        symbol=symbol,
        name=name,
        price=(float(price) if price is not None else None),
        ts=time.time(),
    )
    _price.set(symbol, snap)
    return snap


def get_changes(
    symbol: str,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """(%1h,%24h,%7d) from a 7d/5m history window."""
    symbol = _norm(symbol)
    h = _hist.get(symbol)
    if h is None:
        try:
            t = yf.Ticker(symbol)
            h = t.history(period="7d", interval="5m")
            _hist.set(symbol, h)
        except Exception:
            h = None
    if h is None or h.empty:
        return (None, None, None)

    def pct(minutes: int):
        n = max(1, int(minutes / 5))
        w = h.tail(n)
        if w.empty:
            return None
        a, b = float(w["Close"].iloc[0]), float(w["Close"].iloc[-1])
        if a == 0.0:
            return None
        return (b - a) * 100.0 / a

    return (pct(60), pct(24 * 60), pct(7 * 24 * 60))


# ------------------------------------------------------------------------------
# Fallback providers
# ------------------------------------------------------------------------------
def _fallback_alpha_vantage(symbol: str) -> Optional[PriceSnapshot]:
    api_key = getattr(settings, "ALPHAVANTAGE_API_KEY", None)
    if not api_key:
        return None
    url = "https://www.alphavantage.co/query"
    params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": api_key}
    try:
        with httpx.Client(timeout=6.0) as c:
            r = c.get(url, params=params)
            r.raise_for_status()
            data = r.json().get("Global Quote") or {}
            p = data.get("05. price")
            if not p:
                return None
            price = float(p)
            snap = PriceSnapshot(
                symbol=symbol, name=symbol, price=price, ts=time.time()
            )
            return snap
    except Exception:
        return None


_COINGECKO_MAP = {
    "BTC-USD": "bitcoin",
    "ETH-USD": "ethereum",
    "SOL-USD": "solana",
}


def _fallback_coingecko(symbol: str) -> Optional[PriceSnapshot]:
    cid = _COINGECKO_MAP.get(symbol.upper())
    if not cid:
        return None
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": cid, "vs_currencies": "usd"}
    try:
        with httpx.Client(timeout=6.0) as c:
            r = c.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            price = data.get(cid, {}).get("usd")
            if price is None:
                return None
            snap = PriceSnapshot(
                symbol=symbol, name=cid.title(), price=float(price), ts=time.time()
            )
            return snap
    except Exception:
        return None
