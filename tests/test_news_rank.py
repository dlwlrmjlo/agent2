# tests/test_news_rank.py
from datetime import datetime, timezone

def _ts(x: int) -> float:
    return float(x * 60)

def _import_ranker():
    import app.core.news_rank as nr
    return nr.rank_news_for_event

def test_temporal_first_and_missing_ts_goes_last(monkeypatch):
    """
    Ítem nuevo dentro de ventana debe ir primero; el que no tiene ts no se descarta pero debe quedar al final.
    """
    import app.core.news_rank as nr
    # Evento en t=200; fijamos ventana BEFORE=50 min (~3000s) y AFTER=10 min (~600s)
    # De esta forma t=200 está dentro, t=100 queda fuera.
    event_ts = _ts(200)
    items = [
        {"title": "MSFT surges after earnings", "url": "u1", "publisher": "Reuters", "ts": _ts(100)},  # fuera de ventana
        {"title": "MSFT new guidance beats",   "url": "u2", "publisher": "Reuters", "ts": _ts(200)},  # dentro
        {"title": "MSFT minor note",           "url": "u3", "publisher": "Reuters"},                  # sin ts
    ]
    monkeypatch.setattr(nr, "get_ticker_news", lambda q, limit=20: items, raising=False)

    rank_news_for_event = _import_ranker()
    out = rank_news_for_event("MSFT", event_ts, window_before_min=50, window_after_min=10, limit=3)

    titles = [x["title"] for x in out]
    assert titles[0] == "MSFT new guidance beats"     # el in-window va primero
    assert titles[-1] == "MSFT minor note"            # sin ts queda al final
    assert out[0]["in_window"] is True
    assert out[1]["in_window"] is False

def test_window_filter_prefers_in_window(monkeypatch):
    """
    Un ítem dentro de ventana debe outrankear a otro similar fuera de ventana.
    """
    import app.core.news_rank as nr
    event_ts = _ts(1000)
    in_window  = {"title": "TSLA beats", "url": "a", "publisher": "Reuters", "ts": _ts(995)}   # dentro
    out_window = {"title": "TSLA old",   "url": "b", "publisher": "Reuters", "ts": _ts(1000-10000)}  # muy fuera

    monkeypatch.setattr(nr, "get_ticker_news",
                        lambda q, limit=20: [out_window, in_window], raising=False)

    out = nr.rank_news_for_event("TSLA", event_ts, limit=2)
    assert out[0]["title"] == "TSLA beats"
    assert out[0]["in_window"] is True
    assert out[1]["in_window"] is False

def test_trust_whitelist_boost(monkeypatch):
    """
    A igualdad de tiempo y match, fuente whitelisted (Reuters) debe rankear más alto que una desconocida.
    """
    import app.core.news_rank as nr
    event_ts = _ts(500)
    whitelisted = {"title": "AAPL jumps", "url": "w", "publisher": "Reuters",     "ts": _ts(500)}
    unknown     = {"title": "AAPL jumps", "url": "x", "publisher": "Random Blog", "ts": _ts(500)}

    monkeypatch.setattr(nr, "get_ticker_news",
                        lambda q, limit=20: [unknown, whitelisted], raising=False)

    out = nr.rank_news_for_event("AAPL", event_ts, limit=2)
    assert out[0]["source"] == "Reuters"         # tu ranker normaliza 'publisher' -> 'source'
    assert out[0]["score"] >= out[1]["score"]
