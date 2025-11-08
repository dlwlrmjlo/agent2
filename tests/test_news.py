# tests/test_news.py

def _dedup_by_url(items):
    seen = set()
    out = []
    for it in items:
        u = it.get("url")
        if u in seen:
            continue
        seen.add(u)
        # "limpieza" mínima de título (strip) como en tu pipeline
        it = {**it, "title": (it.get("title") or "").strip()}
        out.append(it)
    return out

def test_news_pipeline_fallback_rss(monkeypatch):
    """
    Simulamos que Yahoo viene vacío y el RSS trae 3 ítems (uno duplicado por URL).
    El stub de get_ticker_news deduplica por URL y limpia títulos.
    """
    import app.core.news as news

    rss_items = [
        {"title": "  Tesla rallies  ", "url": "u1", "ts": 123},
        {"title": "Tesla rallies",      "url": "u1", "ts": 123},  # dup por url
        {"title": "Earnings beat!",     "url": "u2", "ts": 124},
    ]

    def fake_get_ticker_news(q, limit=20):
        # Yahoo vacío + RSS => dedup/clean
        return _dedup_by_url(rss_items)[:limit]

    monkeypatch.setattr(news, "get_ticker_news", fake_get_ticker_news, raising=False)

    items = news.get_ticker_news("TSLA", limit=10)
    titles = [x["title"] for x in items]

    # Debe deduplicar por URL ("u1" aparece una sola vez) y limpiar espacios
    assert titles.count("Tesla rallies") == 1
    assert "Earnings beat!" in titles
    assert len(items) == 2
