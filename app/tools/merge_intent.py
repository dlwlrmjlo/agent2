#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge telemetry (data/intent.jsonl) with synthetic (data/intent.synthetic.jsonl),
deduplicate by text, and optionally rebalance per class.

Usage:
  python -m app.tools.merge_intent \
    --telemetry data/intent.jsonl \
    --synthetic data/intent.synthetic.jsonl \
    --out data/intent.merged.jsonl \
    --per_class 1000
"""
import os, json, argparse
from collections import defaultdict

def read_jsonl(path):
    rows = []
    if not path or not os.path.exists(path):
        return rows
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                r = json.loads(s)
                if 'text' in r and 'label' in r:
                    rows.append({"text": r['text'], "label": int(r['label'])})
            except json.JSONDecodeError:
                pass
    return rows

def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

def dedup(rows):
    seen = set(); out = []
    for r in rows:
        t = (r.get('text') or '').strip()
        if not t or t in seen:
            continue
        seen.add(t)
        out.append({"text": t, "label": int(r.get('label', 0))})
    return out

def rebalance(rows, per_class=None):
    if not per_class:
        return rows
    buckets = defaultdict(list)
    for r in rows:
        buckets[int(r['label'])].append(r)
    out = []
    for lab, items in buckets.items():
        if per_class and len(items) > per_class:
            out.extend(items[:per_class])
        else:
            out.extend(items)
    # keep stable-ish
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--telemetry', default='data/intent.jsonl')
    ap.add_argument('--synthetic', default='data/intent.synthetic.jsonl')
    ap.add_argument('--out', default='data/intent.merged.jsonl')
    ap.add_argument('--per_class', type=int, default=None)
    args = ap.parse_args()

    tel = read_jsonl(args.telemetry)
    syn = read_jsonl(args.synthetic)
    merged = dedup(tel + syn)
    merged = rebalance(merged, per_class=args.per_class)
    write_jsonl(args.out, merged)
    print(f'OK -> {args.out} ({len(merged)} filas; tel={len(tel)}, syn={len(syn)})')

if __name__ == '__main__':
    main()

