#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a balanced intent dataset (es-CL) with hard negatives / edge cases.
Output: data/intent.jsonl
"""
import json, os, random, itertools

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
os.makedirs("data", exist_ok=True)

# Minimal symbol/name pool (expand si quieres)
EQUITIES = ["TSLA","GOOGL","AAPL","MSFT","NVDA","AMZN","META","AMD","NFLX","SQM"]
NAMES = ["tesla","google","apple","microsoft","nvidia","amazon","meta","amd","netflix","sqm"]
CRYPTO = ["BTC-USD","ETH-USD","SOL-USD"]

TEMPLATES = {
    1: [  # FINANCIERO
        "precio de {name}",
        "cotización {sym}",
        "cuánto vale {name} hoy",
        "precio {name} ahora",
        "quote {sym}",
        "valor de {name}",
    ],
    2: [  # ALERTA
        "avísame si {name} cae de {thr}",
        "alerta cuando {sym} supere {thr}",
        "notificar si {name} baja de {thr}",
        "si {sym} sube de {thr}, avísame",
        "cuando {name} rompa {thr} me avisas",
    ],
    0: [  # GENERAL
        "qué pasó con {name}",
        "por qué se movió {name}",
        "explica el movimiento de {name}",
        "qué se dice de {sym} en las noticias",
        "contexto de {name} hoy",
        "últimas novedades de {sym}",
    ],
}

HARD_NEG = [
    # No-alerta aunque diga sube/baja (sin umbral)
    ("dicen que {name} sube fuerte", 0),
    ("parece que {name} baja por resultados", 0),
    # Mixtas: precio + alerta → etiqueta 2 (prioriza regla)
    ("precio de {name} y avísame si baja de {thr}", 2),
    # Ruido/coloquial
    ("cáchate el precio de {name}", 1),
]

def sample_thr():
    return random.choice([50, 100, 150, 200, 250, 300, 500, 1000])

def make_row(t, lab, sym, name):
    txt = t.format(sym=sym, name=name, thr=sample_thr())
    return {"text": txt, "label": lab}

rows = []
pool = list(zip(EQUITIES, NAMES)) + [(c, c.split("-")[0].lower()) for c in CRYPTO]

# Balanced classes
per_class = 250  # ajusta tamaño (→ 750 filas)
for lab in [0,1,2]:
    for sym,name in random.sample(pool, k=min(len(pool), len(pool))):
        for _ in range(per_class // len(pool) + 1):
            t = random.choice(TEMPLATES[lab])
            rows.append(make_row(t, lab, sym, name))

# Hard negatives & edge cases
for t, lab in HARD_NEG:
    for sym,name in random.sample(pool, k= min(8,len(pool))):
        rows.append(make_row(t, lab, sym, name))

random.shuffle(rows)
rows = rows[:800]  # cap

with open("data/intent.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"OK -> data/intent.jsonl ({len(rows)} filas)")

