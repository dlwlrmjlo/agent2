# app/core/telemetry.py
# Append to the SAME dataset (data/intent.jsonl) using the same schema.

from __future__ import annotations
import json, os, time, threading

_LOCK = threading.RLock()
BASE_DIR = os.environ.get("DATA_DIR", "data")
JSONL_PATH = os.path.join(BASE_DIR, "intent.jsonl")  # <- MISMO ARCHIVO
os.makedirs(BASE_DIR, exist_ok=True)

def append_intent_event(text: str, label: int) -> None:
    """
    Append {"text": ..., "label": ...} to data/intent.jsonl.
    We also keep a timestamped comment field for traceability.
    """
    rec = {"text": (text or "").strip()[:500], "label": int(label)}
    # Optional: keep a lightweight meta line (ignored by trainers if they read only json per line)
    # Si NO quieres meta, elimina "meta".
    # rec = {"text": (text or "").strip()[:500], "label": int(label), "meta": {"ts": int(time.time())}}

    line = json.dumps(rec, ensure_ascii=False)
    with _LOCK:
        with open(JSONL_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
