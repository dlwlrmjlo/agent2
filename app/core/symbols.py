# app/core/symbols.py
# Resolve free-text to a valid tradable symbol using Yahoo Finance search + yfinance validation.

from __future__ import annotations
from typing import Optional, Iterable
import re, httpx, yfinance as yf

_YF_SEARCH = "https://query1.finance.yahoo.com/v1/finance/search"

def _looks_like_symbol(s: str) -> bool:
    return bool(re.fullmatch(r"[A-Z0-9.\-]{1,12}", s or ""))

def _is_valid_symbol(sym: str) -> bool:
    try:
        t = yf.Ticker(sym)
        # fast check: any of these present (varía por activo)
        fi = getattr(t, "fast_info", {}) or {}
        if fi.get("lastPrice") is not None:
            return True
        # fallback: try tiny history
        h = t.history(period="1d", interval="1d")
        return not h.empty
    except Exception:
        return False

def _pick_best_quote(quotes: Iterable[dict]) -> Optional[str]:
    # Prefer equities / crypto / ETFs with strong score
    preferred = {"EQUITY", "CRYPTOCURRENCY", "ETF", "MUTUALFUND", "INDEX"}
    best = None
    best_score = -1
    for q in quotes or []:
        qt = (q.get("quoteType") or "").upper()
        sym = (q.get("symbol") or "").upper()
        score = int(q.get("score") or 0)
        if not sym: 
            continue
        if qt in preferred:
            score += 10
        if score > best_score:
            best, best_score = sym, score
    return best

def resolve_symbol(query: str) -> Optional[str]:
    """
    1) If looks like a symbol and validates -> return it.
    2) Else call Yahoo search, pick best candidate, and validate.
    3) For cryptos: if 'BTC' validates false, try 'BTC-USD' heuristic (only then).
    """
    q = (query or "").strip().upper()

    # direct symbol path
    if _looks_like_symbol(q) and _is_valid_symbol(q):
        return q

    # Yahoo search
    try:
        with httpx.Client(timeout=6.0, headers={"User-Agent":"Mozilla/5.0"}) as c:
            r = c.get(_YF_SEARCH, params={"q": q, "quotesCount": 6, "newsCount": 0})
            r.raise_for_status()
            data = r.json()
    except Exception:
        data = {}

    sym = _pick_best_quote(data.get("quotes") or [])
    if sym and _is_valid_symbol(sym):
        return sym

    # Minimal crypto heuristic ONLY if query is a plain crypto ticker-like
    if q in {"BTC","ETH","SOL","DOGE","ADA"}:
        guess = f"{q}-USD"
        if _is_valid_symbol(guess):
            return guess

    return None
