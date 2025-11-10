#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a balanced intent dataset (es-CL) with hard negatives / edge cases.
Output: data/intent.synthetic.jsonl (avoid clobbering real telemetry)
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

# Extra coverage: generate more general (explain/news) and variants
EXTRA_GENERAL = [
    "qu�� pas�� con {sym} hoy",
    "por qu�� se movi�� {name}",
    "por que cay�� {name}",
    "por qu�� subi�� {name}",
    "expl��came {name}",
    "explain {sym}",
    "drivers de {sym}",
    "razones de la ca��da de {name}",
    "qu�� dispar�� a {name}",
    "qu�� motiv�� la suba de {name}",
    "qu�� movi�� a {name} hoy",
    "{sym} hoy, qu�� pas��",
    "noticias de {name}",
    "��ltimas noticias de {sym}",
    "titulares de {name}",
    "news {sym}",
    "novedades de {name}",
    "qu�� dijeron de {name}",
    "��ltimas de {sym}",
    "{sym} hoy",
    "{name} hoy",
    "resumen de {sym}",
    "qu�� hay de nuevo en {name}",
]
EXTRA_FIN = [
    "cuanto est�� {sym}",
    "precio {sym}",
    "precio actual de {name}",
    "cierre de {name}",
]
EXTRA_ALERT = [
    "avisame cuando {sym} cruce {thr}",
    "alerta si {name} perfora {thr}",
]

def _gen_from_templates(templates, label, reps=1):
    for sym,name in random.sample(pool, k=min(len(pool), len(pool))):
        for _ in range(reps):
            t = random.choice(templates)
            rows.append(make_row(t, label, sym, name))

# Generate extras (smaller volume than main)
_gen_from_templates(EXTRA_GENERAL, 0, reps=max(1, per_class // len(pool)))
_gen_from_templates(EXTRA_FIN,     1, reps=max(1, per_class // (2*len(pool))))
_gen_from_templates(EXTRA_ALERT,   2, reps=max(1, per_class // (2*len(pool))))

# Hard negatives & edge cases
for t, lab in HARD_NEG:
    for sym,name in random.sample(pool, k= min(8,len(pool))):
        rows.append(make_row(t, lab, sym, name))

# Additional edge cases to reinforce distinctions
EXTRA_NEG = [
    ("dame noticias de {sym}", 0),
    ("titulares recientes de {name}", 0),
    ("por qu�� {name} subi�� tanto", 0),
    ("por qu�� {name} baj�� hoy", 0),
    ("precio y noticias de {sym}", 1),
    ("qu�� pasa con el precio de {name}", 0),
]
for t, lab in EXTRA_NEG:
    for sym,name in random.sample(pool, k=min(6, len(pool))):
        rows.append(make_row(t, lab, sym, name))

# Add explicit EXPLAIN (3) and NEWS (4) classes to support 5-class adapter
EXPLAIN_TMPL = [
    "que paso con {name}",
    "que paso con {sym} hoy",
    "por que se movio {name}",
    "por que cayo {name}",
    "por que subio {name}",
    "explica el movimiento de {name}",
    "explicame {name}",
    "drivers de {sym}",
]
NEWS_TMPL = [
    "noticias de {name}",
    "ultimas noticias de {sym}",
    "titulares de {name}",
    "news {sym}",
    "novedades de {name}",
    "que dijeron de {name}",
]
for sym,name in random.sample(pool, k=min(len(pool), len(pool))):
    for _ in range(max(1, per_class // len(pool))):
        rows.append(make_row(random.choice(EXPLAIN_TMPL), 3, sym, name))
        rows.append(make_row(random.choice(NEWS_TMPL), 4, sym, name))

random.shuffle(rows)
rows = rows[:1200]  # cap

with open("data/intent.synthetic.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"OK -> data/intent.synthetic.jsonl ({len(rows)} filas)")

