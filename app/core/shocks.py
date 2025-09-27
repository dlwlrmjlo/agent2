# app/core/shocks.py
# Purpose: find recent price shocks (Δ15m / Δ60m) for a ticker.

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
from datetime import datetime, timezone, timedelta
import pandas as pd
from app.core.market import get_changes, get_last_price

@dataclass
class ShockEvent:
    symbol: str
    ts: float                # unix seconds (now)
    delta_15m: Optional[float]
    delta_60m: Optional[float]
    threshold_hit: str       # "15m" | "60m" | "none"

def _threshold_check(d15: Optional[float], d60: Optional[float],
                     thr15: float, thr60: float) -> str:
    """
    Return which threshold was hit (absolute move).
    """
    if d15 is not None and abs(d15) >= thr15:
        return "15m"
    if d60 is not None and abs(d60) >= thr60:
        return "60m"
    return "none"

def get_last_shock(symbol: str,
                   thr15: float = 1.5,   # % move in 15 minutes to consider shock
                   thr60: float = 3.0    # % move in 60 minutes to consider shock
                   ) -> ShockEvent:
    """
    Compute simple shock using cached market deltas.
    Note: get_changes() returns (%1h, %24h, %7d). We approximate 15m using price now
    vs price 60m window tail slice if available; as a first MVP, we use 60m only and flag 15m as None.
    """
    # Reuse what we have: (%1h, %24h, %7d)
    d1h, _, _ = get_changes(symbol)
    # MVP: we don't have Δ15m from market.py; set None for now (can add later from 5m history)
    d15 = None

    hit = _threshold_check(d15, d1h, thr15, thr60)
    now_ts = get_last_price(symbol).ts
    return ShockEvent(symbol=symbol, ts=now_ts, delta_15m=d15, delta_60m=d1h, threshold_hit=hit)
