# app/core/news_rank.py
# Purpose: rank news near a shock event using simple, explainable rules.

from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import math
import re

from app.core.news import get_ticker_news

_WHITELIST = {
    "Reuters","Bloomberg","WSJ","The Wall Street Journal","Financial Times","FT",
    "CNBC","AP","Associated Press","Yahoo Finance","MarketWatch","The Verge",
    "Forbes","Barron's","Bloomberg Opinion","Seeking Alpha"
}

def _parse_ts(item: Dict[str, Any]) -> float | None:
    """
    Try to read a unix timestamp from the news item.
    get_ticker_news() may return 'ts' when Yahoo API exists. For RSS fallback it may not exist.
    """
    ts = item.get("ts")
    if isinstance(ts, (int, float)):
        return float(ts)
    # Optional: support RFC2822/RFC3339 if you extend news.py later
    return None

def _has_ticker_in_title(title: str, q: str) -> bool:
    t = (title or "").upper()
    q = (q or "").upper()
    if not t or not q: 
        return False
    # Exact ticker or company name substring
    return (q in t) or bool(re.search(rf"\b{re.escape(q)}\b", t))

def _source_trust(s: str | None) -> float:
    if not s: 
        return 0.2
    return 1.0 if s in _WHITELIST else 0.5

def rank_news_for_event(q: str, event_ts: float,
                        window_before_min: int = 90,
                        window_after_min: int = 60,
                        limit: int = 3) -> List[Dict[str, Any]]:
    """
    Pull recent news via get_ticker_news, filter by time window around the event,
    score them, and return Top-N with 'confidence' labels.
    """
    items = get_ticker_news(q, limit=20)  # pull a bit more, we'll filter
    start = event_ts - window_before_min * 60
    end   = event_ts + window_after_min * 60

    scored = []
    for it in items:
        title = it.get("title") or ""
        src   = it.get("publisher") or it.get("source")
        ts    = _parse_ts(it)

        # Time filter: if we have no ts, keep but with penalty
        in_window = (ts is not None and start <= ts <= end)
        time_bonus = 1.0 if in_window else 0.3

        # Title/ticker match
        match_bonus = 1.0 if _has_ticker_in_title(title, q) else 0.4

        trust = _source_trust(src)

        # Simple explainable score
        score = 0.45 * time_bonus + 0.35 * trust + 0.20 * match_bonus

        scored.append({
            **it,
            "score": round(score, 3),
            "in_window": bool(in_window),
            "source": src
        })

    # Sort by score then prefer in-window when tied
    scored.sort(key=lambda x: (x["score"], x["in_window"]), reverse=True)
    top = scored[:limit]

    # Confidence label
    def conf(s): 
        return "alta" if s >= 0.8 else ("media" if s >= 0.6 else "baja")
    for x in top:
        x["confidence"] = conf(x["score"])

    return top
