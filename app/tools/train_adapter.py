#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Train a lightweight intent adapter (SBERT + LogisticRegression) on CPU.
- Input: data/intent.jsonl ({"text": ..., "label": 0|1|2})
- Output artifacts: models/intent_adapter/{encoder.txt, lr.joblib, label_map.json, stats.json}
"""

import os, json, argparse, time
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score
from sklearn.model_selection import train_test_split
from joblib import dump
from sentence_transformers import SentenceTransformer

ENCODER_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # small, multilingual, CPU-friendly

def read_jsonl(path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: 
                continue
            rows.append(json.loads(line))
    return rows

def encode_texts(model: SentenceTransformer, texts: List[str], batch_size: int = 64) -> np.ndarray:
    """Return L2-normalized embeddings (float32)."""
    embs = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return embs.astype("float32")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default="data/intent.jsonl", help="path to jsonl with {text,label}")
    ap.add_argument("--outdir", default="models/intent_adapter", help="artifacts output dir")
    ap.add_argument("--test_size", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    data = read_jsonl(args.train)
    if not data:
        raise SystemExit(f"No data in {args.train}")

    X = [r["text"] for r in data]
    y = [int(r["label"]) for r in data]

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=args.test_size, random_state=args.seed, stratify=y)

    print(f"[INFO] Loading encoder: {ENCODER_NAME}")
    enc = SentenceTransformer(ENCODER_NAME)

    print("[INFO] Encoding train...")
    Z_tr = encode_texts(enc, X_tr)
    print("[INFO] Encoding test...")
    Z_te = encode_texts(enc, X_te)

    print("[INFO] Fitting LogisticRegression...")
    clf = LogisticRegression(
        C=2.0,                 # slightly stronger regularization than default
        max_iter=300,          # avoid convergence warnings
        n_jobs=1,              # CPU single-process (embeddings were the heavy part)
        class_weight="balanced"
    )
    t0 = time.time()
    clf.fit(Z_tr, y_tr)
    train_s = round(time.time() - t0, 2)

    y_pred = clf.predict(Z_te)
    y_proba = clf.predict_proba(Z_te)
    acc = accuracy_score(y_te, y_pred)
    f1m = f1_score(y_te, y_pred, average="macro")
    # Allow up to 5 labels if present in data
    all_labels = sorted({0,1,2,3,4}.intersection(set(y_tr + y_te))) or [0,1,2]
    cm = confusion_matrix(y_te, y_pred, labels=all_labels).tolist()

    print("\n=== Eval ===")
    print(f"Accuracy: {acc:.4f} | F1-macro: {f1m:.4f}")
    print("Confusion (rows=true, cols=pred):", cm)
    print(classification_report(y_te, y_pred, digits=3))

    # Save artifacts
    dump(clf, os.path.join(args.outdir, "lr.joblib"))
    with open(os.path.join(args.outdir, "encoder.txt"), "w", encoding="utf-8") as f:
        f.write(ENCODER_NAME + "\n")
    with open(os.path.join(args.outdir, "label_map.json"), "w", encoding="utf-8") as f:
        json.dump({
            "labels": all_labels,
            "names": {"0":"general","1":"financiero","2":"alerta","3":"explain","4":"news"}
        }, f)

    with open(os.path.join(args.outdir, "stats.json"), "w", encoding="utf-8") as f:
        json.dump({
            "train_file": args.train,
            "encoder": ENCODER_NAME,
            "samples": len(data),
            "acc": acc,
            "f1_macro": f1m,
            "cm": cm,
            "train_seconds": train_s
        }, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Artifacts saved in {args.outdir}")

if __name__ == "__main__":
    main()

