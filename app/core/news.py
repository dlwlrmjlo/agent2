# app/core/news.py
# Clean ticker news: resolve name->symbol, Yahoo news first, RSS fallback, no placeholders.

from __future__ import annotations
from typing import List, Dict, Any, Optional
import time, threading, html, re
import xml.etree.ElementTree as ET
import httpx, yfinance as yf
from app.core.config import settings

WHITELIST = {"reuters.com","bloomberg.com","finance.yahoo.com","wsj.com","ft.com","cnbc.com","theverge.com","techcrunch.com","seekingalpha.com"}
BLACKLIST = {"people.com","usmagazine.com","usweekly.com","tmz.com","infobae.com"}
NAME2SYM = {"TESLA":"TSLA","MICROSOFT":"MSFT","APPLE":"AAPL","AMAZON":"AMZN","GOOGLE":"GOOGL","ALPHABET":"GOOGL","META":"META","NVIDIA":"NVDA","SQM":"SQM"}

class _TTLCache:
    def __init__(self, ttl_s=300, maxsize=512):
        self.ttl=ttl_s; self.maxsize=maxsize; self._data={}; self._lock=threading.RLock()
    def get(self,k):
        with self._lock:
            v=self._data.get(k)
            if not v: return None
            val,ts=v
            if time.time()-ts>self.ttl: self._data.pop(k,None); return None
            return val
    def set(self,k,val):
        with self._lock:
            if len(self._data)>=self.maxsize: self._data.clear()
            self._data[k]=(val,time.time())

_cache = _TTLCache(settings.NEWS_CACHE_TTL_S)

def _clean(s:str)->str:
    s = html.unescape(s or "")
    s = re.sub(r"\s+"," ",s).strip()
    return s[:280]

def _domain(url:str)->str:
    try:
        host = url.split("/")[2].lower()
        return re.sub(r"^www\.","",host)
    except Exception:
        return ""

def _is_relevant(it:Dict[str,Any], keywords:List[str])->bool:
    d = _domain(it.get("link","") or "")
    if d in BLACKLIST: return False
    if WHITELIST and d not in WHITELIST:
        title = (it.get("title") or "").lower()
        return any(k.lower() in title for k in keywords)
    return True

def _guess_symbol(q:str)->Optional[str]:
    u=(q or "").strip().upper()
    if u in NAME2SYM: return NAME2SYM[u]
    if re.fullmatch(r"[A-Z0-9.\-]{1,12}",u): return u
    return None

def _rss_items(query:str, limit:int)->List[Dict[str,Any]]:
    url = f"https://news.google.com/rss/search?q={query}&hl=es-419&gl=CL&ceid=CL:es-419"
    try:
        with httpx.Client(timeout=8.0, headers={"User-Agent":"Mozilla/5.0"}) as c:
            r = c.get(url); r.raise_for_status()
            root = ET.fromstring(r.text)
            out=[]
            for item in root.findall(".//item"):
                title=_clean(item.findtext("title") or "")
                link=(item.findtext("link") or "").strip()
                if not title or not link: continue
                pub=item.findtext("pubDate") or item.findtext("published")
                out.append({"title":title,"link":link,"summary":"","published":pub,"source":None})
                if len(out)>=limit: break
            return out
    except Exception:
        return []

def _merge_dedup(items:List[Dict[str,Any]], limit:int)->List[Dict[str,Any]]:
    seen=set(); out=[]
    for it in items:
        key=(it.get("title"), it.get("link"))
        if not key[0] or not key[1]: continue
        if key in seen: continue
        seen.add(key); out.append(it)
        if len(out)>=limit: break
    return out

def get_ticker_news(q:str, limit:int=5)->List[Dict[str,Any]]:
    q=(q or "").strip()
    key=f"news:{q.upper()}:{limit}"
    cached=_cache.get(key)
    if cached is not None: return cached

    symbol=_guess_symbol(q)
    name_q=q.title() or (symbol or "")
    keywords=[name_q]+([symbol] if symbol else [])
    out:List[Dict[str,Any]]=[]

    # 1) Yahoo news via yfinance (if symbol)
    if symbol:
        try:
            t=yf.Ticker(symbol)
            for n in (getattr(t,"news",None) or []):
                title=_clean(n.get("title","")); link=(n.get("link","") or "").strip()
                if not title or not link: continue
                out.append({"title":title,"link":link,"summary":_clean(n.get("summary","") or n.get("publisher","")),
                            "published":n.get("providerPublishTime") or n.get("pubDate"),
                            "source":n.get("publisher")})
                if len(out)>=limit: break
        except Exception:
            pass

    # 2) Fallback RSS
    if len(out)<limit:
        q_terms=[]
        if symbol: q_terms.append(symbol)
        if name_q: q_terms.append(f"\"{name_q}\"")
        query = re.sub(r"\s+","+", " OR ".join(q_terms) + " stock when:7d")
        rss = _rss_items(query, limit*3)
        rss = [it for it in rss if _is_relevant(it, keywords)]
        out.extend(_merge_dedup(rss, limit - len(out)))

    _cache.set(key, out)
    return out
