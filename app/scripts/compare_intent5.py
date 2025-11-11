#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare LLM vs Adapter on 5-class intent (0..4).

Usage:
  python -m app.scripts.compare_intent5 data/intent.merged.jsonl --out_dir data

Writes:
  <out_dir>/pred_llm.5.jsonl
  <out_dir>/pred_adapter.5.jsonl
  <out_dir>/intent_eval_report_5.md
  <out_dir>/intent_eval_mismatches_5.jsonl
"""

import os, json, time, argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

from app.api.services import classify_intent
from app.core.config import settings


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: str, rows: List[Dict[str, Any]]):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def p50_p95(xs: List[float]) -> Tuple[float, float]:
    if not xs: return (0.0, 0.0)
    arr = np.array(xs, dtype=float)
    return float(np.percentile(arr, 50)), float(np.percentile(arr, 95))


async def run_once(rows: List[Dict[str, Any]], mode: str, out_path: str):
    prev = settings.INTENT_MODE
    settings.INTENT_MODE = mode

    preds, lats, out_rows = [], [], []
    for r in rows:
        t0 = time.perf_counter()
        y = await classify_intent(r["text"])  # expected 0..4 when LLM; adapter may be 0..2 if not retrained
        dt = (time.perf_counter() - t0) * 1000.0
        preds.append(int(y))
        lats.append(dt)
        out_rows.append({
            "text": r["text"], "label": int(r["label"]),
            "pred": int(y), "mode": mode, "lat_ms": round(dt, 3)
        })

    settings.INTENT_MODE = prev

    y_true = [int(r["label"]) for r in rows]
    acc = accuracy_score(y_true, preds)
    f1m = f1_score(y_true, preds, average="macro")
    used_labels = sorted(set([0,1,2,3,4]) & (set(y_true) | set(preds))) or [0,1,2]
    cm = confusion_matrix(y_true, preds, labels=used_labels).tolist()
    p50, p95 = p50_p95(lats)

    write_jsonl(out_path, out_rows)
    return {
        "mode": mode, "acc": acc, "f1_macro": f1m, "cm": cm,
        "labels": used_labels, "p50_ms": p50, "p95_ms": p95,
        "preds": preds, "lat_ms": lats, "out": out_path, "rows": out_rows
    }


def print_block(res: Dict[str, Any]):
    print(f"\nOK -> {res['out']} ({len(res['rows'])} ítems)")
    print(f"Accuracy: {res['acc']:.4f} | F1-macro: {res['f1_macro']:.4f} | "
          f"Lat p50/p95: {int(res['p50_ms'])}/{int(res['p95_ms'])} ms")
    print("Etiquetas:", res.get("labels"))
    print("Matriz de confusión (filas=true, cols=pred):")
    for row in res["cm"]:
        print(" ", row)


def write_report_md(path: str, gold: List[int], r_llm: Dict[str,Any], r_adp: Dict[str,Any], mismatches: List[Dict[str,Any]]):
    def fmt_cm(cm: List[List[int]]):
        return "\n".join(["[" + ", ".join(str(x) for x in row) + "]" for row in cm])

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Intent Eval Report (LLM vs Adapter, 5 clases)\n\n")
        f.write(f"- Items: **{len(gold)}**\n\n")
        f.write("## Resumen de Métricas\n\n")
        f.write("| Modo | Accuracy | F1-macro | Lat p50 (ms) | Lat p95 (ms) |\n")
        f.write("|---|---:|---:|---:|---:|\n")
        f.write(f"| LLM | {r_llm['acc']:.4f} | {r_llm['f1_macro']:.4f} | {r_llm['p50_ms']:.0f} | {r_llm['p95_ms']:.0f} |\n")
        f.write(f"| Adapter | {r_adp['acc']:.4f} | {r_adp['f1_macro']:.4f} | {r_adp['p50_ms']:.0f} | {r_adp['p95_ms']:.0f} |\n\n")
        f.write("## Matrices de confusión (filas=true, columnas=pred)\n\n")
        f.write("**LLM**\n\n```\n" + fmt_cm(r_llm["cm"]) + "\n```\n\n")
        f.write("**Adapter**\n\n```\n" + fmt_cm(r_adp["cm"]) + "\n```\n\n")
        f.write(f"## Mismatches (total {len(mismatches)})\n\n")
        for m in mismatches[:200]:
            f.write(f"- gold={m['gold']} | llm={m['llm_pred']} | adp={m['adp_pred']} | txt: {m['text']}\n")
        if len(mismatches) > 200:
            f.write(f"\n… y {len(mismatches)-200} más.\n")


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp", help="jsonl con {text,label}")
    ap.add_argument("--out_dir", default="data", help="carpeta de salida")
    args = ap.parse_args()

    rows = read_jsonl(args.inp)
    if not rows:
        raise SystemExit(f"Sin datos en {args.inp}")

    y_true = [int(r["label"]) for r in rows]

    r_llm = await run_once(rows, mode="LLM", out_path=os.path.join(args.out_dir, "pred_llm.5.jsonl"))
    print_block(r_llm)

    r_adp = await run_once(rows, mode="ADAPTER", out_path=os.path.join(args.out_dir, "pred_adapter.5.jsonl"))
    print_block(r_adp)

    mismatches = []
    for rl, ra in zip(r_llm["rows"], r_adp["rows"]):
        gold = rl["label"]
        if (rl["pred"] != gold) or (ra["pred"] != gold) or (rl["pred"] != ra["pred"]):
            mismatches.append({
                "text": rl["text"],
                "gold": gold,
                "llm_pred": rl["pred"],
                "adp_pred": ra["pred"]
            })

    report_md = os.path.join(args.out_dir, "intent_eval_report_5.md")
    write_report_md(report_md, y_true, r_llm, r_adp, mismatches)
    write_jsonl(os.path.join(args.out_dir, "intent_eval_mismatches_5.jsonl"), mismatches)

    print("\n==== Resumen comparativo (5 clases) ====")
    print(f"Reporte -> {report_md}")
    print(f"Mismatches -> {os.path.join(args.out_dir, 'intent_eval_mismatches_5.jsonl')}")
    print("Listo.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

