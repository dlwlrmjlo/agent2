# tests/test_explain.py (extra case)
import pytest

def test_explain_handles_llm_timeout(mock_ask_llm, monkeypatch):
    """
    When LLM returns None/empty, brief should degrade with a clear message.
    """
    import app.core.explain as explain

    # Force mock_ask_llm to return empty
    monkeypatch.setattr(explain, "ask_llm", lambda *a, **k: "", raising=False)

    text = explain.build_intraday_brief("TSLA", top_news=[
        {"title": "Minor move", "url": "u1", "ts": 1},
    ])

    assert isinstance(text, str) and text.strip()
    assert "concluyente" in text.lower() or "poco concluy" in text.lower()
