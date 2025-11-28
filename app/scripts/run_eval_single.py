#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[STEP 4: SINGLE PREDICTION]
Este script es una herramienta de utilidad para probar el modelo en caliente.
Permite pasar una frase (string) o un archivo JSONL y ver qué predice el sistema (Adaptador + LLM híbrido).
Útil para debugging rápido.

Uso:
  python app/scripts/run_eval_single.py "precio amd"
"""
import os, sys, json, time, asyncio
import os, sys, json, time, asyncio

# << parche clave: subir a la raíz del repo >>
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from app.api.services import classify_intent

def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s: 
                continue
            try:
                rows.append(json.loads(s))
            except json.JSONDecodeError:
                pass
    return rows

def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def accuracy(y_true, y_pred):
    return sum(int(t==p) for t,p in zip(y_true,y_pred)) / max(1,len(y_true))

def f1_macro(y_true, y_pred, labels=(0,1,2)):
    eps=1e-9; out=[]
    for l in labels:
        tp=sum(1 for t,p in zip(y_true,y_pred) if t==l and p==l)
        fp=sum(1 for t,p in zip(y_true,y_pred) if t!=l and p==l)
        fn=sum(1 for t,p in zip(y_true,y_pred) if t==l and p!=l)
        prec=tp/(tp+fp+eps); rec=tp/(tp+fn+eps)
        out.append((2*prec*rec)/(prec+rec+eps))
    return sum(out)/len(out)

def confusion(y_true,y_pred,labels=(0,1,2)):
    idx={l:i for i,l in enumerate(labels)}
    m=[[0]*len(labels) for _ in labels]
    for t,p in zip(y_true,y_pred):
        if t in idx and p in idx:
            m[idx[t]][idx[p]]+=1
    return m, labels

async def main(inp, out):
    if not inp.endswith(".jsonl") and not os.path.exists(inp):
        # Assume it's a raw string prompt
        print(f"Evaluating single prompt: '{inp}'")
        t0 = time.perf_counter()
        y = int(await classify_intent(inp))
        ms = (time.perf_counter() - t0) * 1000
        print(f"Prediction: {y} | Latency: {ms:.2f} ms")
        return

    rows = read_jsonl(inp)
    preds=[]; y_true=[]; y_pred=[]; lats=[]
    for r in rows:
        t0=time.perf_counter()
        y = int(await classify_intent(r["text"]))
        ms=(time.perf_counter()-t0)*1000
        rec={"text":r["text"],"y_true":int(r["label"]),"y_pred":y,"latency_ms":round(ms,1)}
        preds.append(rec); y_true.append(rec["y_true"]); y_pred.append(y); lats.append(ms)
    write_jsonl(out, preds)
    acc=accuracy(y_true,y_pred); f1=f1_macro(y_true,y_pred)
    lats.sort(); p50=lats[len(lats)//2] if lats else 0; p95=lats[int(len(lats)*0.95)] if lats else 0
    cm, labels = confusion(y_true,y_pred)
    print(f"OK -> {out} ({len(preds)} ítems)")
    print(f"Accuracy: {acc:.4f} | F1-macro: {f1:.4f} | Lat p50/p95: {p50:.0f}/{p95:.0f} ms")
    print("Matriz de confusión (filas=true, cols=pred):", labels)
    for row in cm:
        print("  ", row)

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv)>1 else "data/test.adversarial.jsonl"
    out = sys.argv[2] if len(sys.argv)>2 else "data/pred_baseline.jsonl"
    asyncio.run(main(inp, out))

