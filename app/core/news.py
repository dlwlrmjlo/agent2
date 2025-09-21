# app/core/news.py
# Purpose: clean ticker news with symbol resolution, API-first + RSS fallback, and noise filtering.

from __future__ import annotations
from typing import List, Dict, Any, Optional
import time, threading, html, re
import xml.etree.ElementTree as ET
import httpx
import yfinance as yf

# --- Domain filters (ajusta a gusto) ---
WHITELIST = {
    "reuters.com", "bloomberg.com", "finance.yahoo.com", "wsj.com",
    "ft.com", "cnbc.com", "theverge.com", "techcrunch.com", "seekingalpha.com"
}
BLACKLIST = {"people.com", "usmagazine.com", "usweekly.com", "tmz.com", "infobae.com"}

# --- Nombre común -> símbolo (atajos útiles) ---
NAME2SYM = {
    "TESLA": "TSLA",
    "MICROSOFT": "MSFT",
    "APPLE": "AAPL",
    "AMAZON": "AMZN",
    "GOOGLE": "GOOGL", "ALPHABET": "GOOGL",
    "META": "META",
    "NVIDIA": "NVDA",
    "SQM": "SQM",
}

# --- TTL cache simple ---
class _TTLCache:
    def __init__(self, ttl_s: int = 300, maxsize: int = 512):
        self.ttl = ttl_s
        self.maxsize = maxsize
        self._data: Dict[str, tuple[float, Any]] = {}
        self._lock = threading.RLock()
    def get(self, k: str):
        with self._lock:
            v = self._data.get(k)
            if not v: return None
            val, ts = v
            if time.time() - ts > self.ttl:
                self._data.pop(k, None); return None
            return val
    def set(self, k: str, val: Any):
        with self._lock:
            if len(self._data) >= self.maxsize: self._data.clear()
            self._data[k] = (val, time.time())

_cache = _TTLCache(ttl_s=300)

def _clean(s: str) -> str:
    if not s: return ""
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:280]

def _domain(url: str) -> str:
    try:
        host = url.split("/")[2].lower()
        return re.sub(r"^www\.", "", host)
    except Exception:
        return ""

def _is_relevant(item: Dict[str, Any], keywords: List[str]) -> bool:
    d = _domain(item.get("link", "") or "")
    if d in BLACKLIST: 
        return False
    if WHITELIST and d not in WHITELIST:
        title = (item.get("title") or "").lower()
        return any(k.lower() in title for k in keywords)
    return True

def _guess_symbol(q: str) -> Optional[str]:
    u = (q or "").strip().upper()
    if u in NAME2SYM:
        return NAME2SYM[u]
    if re.fullmatch(r"[A-Z0-9.\-]{1,12}", u):  # ya parece símbolo
        return u
    return None

def _from_rss_item(item: ET.Element) -> Optional[Dict[str, Any]]:
    title = _clean(item.findtext("title") or "")
    link  = (item.findtext("link") or "").strip()
    if not title or not link:
        return None
    pub   = item.findtext("pubDate") or item.findtext("published")
    return {"title": title, "link": link, "summary": "", "published": pub, "source": None}

def _fetch_google_rss(query: str, limit: int) -> List[Dict[str, Any]]:
    # query en es-419/CL para reducir tabloide en español
    url = f"https://news.google.com/rss/search?q={query}&hl=es-419&gl=CL&ceid=CL:es-419"
    try:
        with httpx.Client(timeout=8.0, headers={"User-Agent":"Mozilla/5.0"}) as c:
            r = c.get(url); r.raise_for_status()
            root = ET.fromstring(r.text)
            out: List[Dict[str, Any]] = []
            for item in root.findall(".//item"):
                it = _from_rss_item(item)
                if it: out.append(it)
                if len(out) >= limit: break
            return out
    except Exception:
        return []

def _merge_dedup(items: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    seen = set(); out: List[Dict[str, Any]] = []
    for it in items:
        key = (it.get("title"), it.get("link"))
        if not key[0] or not key[1]:  # descarta vacíos
            continue
        if key in seen: 
            continue
        seen.add(key); out.append(it)
        if len(out) >= limit: break
    return out

def get_ticker_news(q: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    q puede ser símbolo (MSFT) o nombre (Tesla).
    1) Resolver símbolo (si es posible).
    2) yfinance.Ticker(symbol).news (si hay symbol).
    3) Fallback: Google News RSS con query fuerte (symbol OR "Nombre" stock).
    4) Filtrar por whitelist/blacklist; sin placeholders vacíos.
    """
    q = (q or "").strip()
    cache_key = f"news:{q.upper()}:{limit}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    symbol = _guess_symbol(q)             # "TESLA" -> "TSLA"
    name_q = q.title() or (symbol or "")
    keywords = [name_q] + ([symbol] if symbol else [])

    out: List[Dict[str, Any]] = []

    # 1) yfinance (si tenemos symbol)
    if symbol:
        try:
            t = yf.Ticker(symbol)
            items = getattr(t, "news", None) or []
            for n in items:
                title = _clean(n.get("title", ""))
                link  = (n.get("link", "") or "").strip()
                if not title or not link:
                    continue
                out.append({
                    "title": title,
                    "link": link,
                    "summary": _clean(n.get("summary", "") or n.get("publisher", "")),
                    "published": n.get("providerPublishTime") or n.get("pubDate"),
                    "source": n.get("publisher"),
                })
                if len(out) >= limit: break
        except Exception:
            pass

    # 2) Fallback RSS (merge + filtro)
    if len(out) < limit:
        # Query fuerte: SYMBOL OR "Nombre" + stock + ventana reciente
        query_terms = []
        if symbol: query_terms.append(symbol)
        if name_q: query_terms.append(f"\"{name_q}\"")
        query = re.sub(r"\s+", "+", " OR ".join(query_terms) + " stock when:7d")

        rss_items = _fetch_google_rss(query, limit=limit*3)  # traemos extra para filtrar
        # filtro por relevancia/ruido
        rss_items = [it for it in rss_items if _is_relevant(it, keywords)]
        # dedup y recorte final
        rss_items = _merge_dedup(rss_items, limit=limit - len(out))
        out.extend(rss_items)

    _cache.set(cache_key, out)
    return out
