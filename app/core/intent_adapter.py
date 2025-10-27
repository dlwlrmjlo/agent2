# app/core/intent_adapter.py
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional, Tuple, cast
import numpy as np
from joblib import load
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression

_ART_DIR = Path(os.environ.get("INTENT_ADAPTER_DIR", "models/intent_adapter"))

_enc: Optional[SentenceTransformer] = None
_clf: Optional[LogisticRegression] = None

def _load_encoder_name() -> str:
    return (_ART_DIR / "encoder.txt").read_text(encoding="utf-8").strip()

def _lazy_load() -> None:
    global _enc, _clf
    if _enc is None:
        _enc = SentenceTransformer(_load_encoder_name())
    if _clf is None:
        _clf = cast(LogisticRegression, load(_ART_DIR / "lr.joblib"))

def predict(text: str) -> Tuple[int, float]:
    """(label, confidence) con softmax del LR. label ∈ {0,1,2}."""
    _lazy_load()
    assert _enc is not None and _clf is not None
    emb = _enc.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    proba: np.ndarray = _clf.predict_proba(emb)[0]   # shape (3,)
    y = int(np.argmax(proba))
    conf = float(proba[y])
    return y, conf
