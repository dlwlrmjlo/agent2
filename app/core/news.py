# app/core/news.py
# Purpose: provide ticker-related headlines with API-first approach and a safe fallback.
from __future__ import annotations
from typing import List, Dict, Any
import time, threading, httpx, html
import yfinance as yf

class _TTLCache:
    def __init__(self, ttl_s: int = 300, maxsize: int = 512):
        self.ttl = ttl_s
        self.maxsize = maxsize
        self._data = {}
        self._lock = threading.RLock()
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

_cache = _TTLCache(ttl_s=300)

def get_ticker_news(symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    API-first via yfinance.Ticker.news (if available), else fallback to Google News RSS.
    Returns a list of {title, link, publisher, ts}.
    """
    symbol = (symbol or "").upper().strip()
    cache_key = f"news:{symbol}:{limit}"
    cached = _cache.get(cache_key)
    if cached: return cached

    out: List[Dict[str, Any]] = []
    t = yf.Ticker(symbol)
    try:
        # yfinance exposes Yahoo Finance news in some versions
        items = getattr(t, "news", None)
        if items:
            for it in items[:limit]:
                out.append({
                    "title": it.get("title"),
                    "link": it.get("link"),
                    "publisher": it.get("publisher"),
                    "ts": it.get("providerPublishTime")
                })
    except Exception:
        pass

    # Fallback: Google News RSS (public). Keep it light and safe.
    if not out:
        import xml.etree.ElementTree as ET
        q = symbol.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={q}+stock"
        try:
            with httpx.Client(timeout=8.0, headers={"User-Agent":"Mozilla/5.0"}) as c:
                r = c.get(url); r.raise_for_status()
                root = ET.fromstring(r.text)
                for item in root.findall(".//item")[:limit]:
                    title = item.findtext("title") or ""
                    link  = item.findtext("link") or ""
                    out.append({"title": html.unescape(title), "link": link, "publisher": "Google News RSS"})
        except Exception:
            pass

    _cache.set(cache_key, out)
    return out
