# app/core/symbols.py
# Resolve free-text to a valid tradable symbol using Yahoo Finance search + yfinance validation.

from __future__ import annotations
from typing import Optional, Iterable
import re, httpx, yfinance as yf
from app.core.config import settings
from app.core.news import NAME2SYM as _NAME2SYM

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

def resolve_symbol(query: str, trust_direct: Optional[bool] = None) -> Optional[str]:
    """
    Resolve text to a tradable symbol with a fast-path:
      - If `SYMBOL_FAST_MODE` and name-to-symbol mapping matches -> return mapped.
      - If looks like ticker and `SYMBOL_TRUST_TICKER` -> return uppercase token.
      - Else validate with yfinance fast_info/history.
      - Else Yahoo search (short timeout) and validate.
      - Crypto minimal '-USD' heuristic.
    """
    q_raw = (query or "").strip()
    q = q_raw.upper()
    if trust_direct is None:
        trust_direct = bool(settings.SYMBOL_TRUST_TICKER)

    # 0) Name -> symbol mapping (shared with news) for speed
    if settings.SYMBOL_FAST_MODE:
        sym = _NAME2SYM.get(q) or _NAME2SYM.get(q_raw.strip().title()) or _NAME2SYM.get(q_raw.strip().upper())
        if sym:
            return sym

    # 1) Trust direct ticker if allowed -> DISABLED to force validation/search for ambiguous inputs like "INTEL"
    # if trust_direct and _looks_like_symbol(q):
    #     return q

    # 2) Validate direct ticker if present
    if _looks_like_symbol(q) and _is_valid_symbol(q):
        return q

    # 3) Yahoo search (short timeout)
    try:
        with httpx.Client(timeout=float(settings.SYMBOL_HTTP_TIMEOUT_S), headers={"User-Agent":"Mozilla/5.0"}) as c:
            r = c.get(_YF_SEARCH, params={"q": q, "quotesCount": 6, "newsCount": 0})
            r.raise_for_status()
            data = r.json()
    except Exception:
        data = {}

    sym = _pick_best_quote(data.get("quotes") or [])
    if sym and _is_valid_symbol(sym):
        return sym

    # 4) Minimal crypto heuristic ONLY if query is a plain crypto ticker-like
    if q in {"BTC","ETH","SOL","DOGE","ADA"}:
        guess = f"{q}-USD"
        if _is_valid_symbol(guess):
            return guess

    return None
