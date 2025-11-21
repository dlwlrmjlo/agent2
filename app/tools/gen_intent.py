#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a balanced intent dataset (5 clases) with edge cases.
Clases:
 0 = general (no precio/alerta/explain/news)
 1 = financiero (precio/cotizacion)
 2 = alerta (umbral)
 3 = explain (por que/que paso)
 4 = news (titulares)
"""

import json
import os
import random

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
os.makedirs("data", exist_ok=True)

EQUITIES = [
    "TSLA",
    "GOOGL",
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "AMD",
    "NFLX",
    "SQM",
]
NAMES = [
    "tesla",
    "google",
    "apple",
    "microsoft",
    "nvidia",
    "amazon",
    "meta",
    "amd",
    "netflix",
    "sqm",
]
CRYPTO = ["BTC-USD", "ETH-USD", "SOL-USD"]

TEMPLATES = {
    0: [
        "que es un modelo de lenguaje",
        "como funciona el scraping web",
        "ayudame a resumir un articulo",
        "reformula esta busqueda de {name}",
        "busca contexto sobre {name}",
        "haz un resumen sobre inteligencia artificial",
        "que sabes de {name}",
        "ayuda con tarea sobre {name}",
    ],
    1: [
        "precio de {name}",
        "cotizacion {sym}",
        "cuanto vale {name} hoy",
        "precio {name} ahora",
        "quote {sym}",
        "valor de {name}",
        "cual es el precio de {sym}",
    ],
    2: [
        "avisame si {name} cae de {thr}",
        "alerta cuando {sym} supere {thr}",
        "notificar si {name} baja de {thr}",
        "si {sym} sube de {thr}, avisame",
        "cuando {name} rompa {thr} me avisas",
        "avisame si {sym} baja de {thr}",
    ],
    3: [
        "que paso con {name}",
        "por que se movio {name}",
        "por que cayo {name}",
        "por que subio {name}",
        "explica el movimiento de {name}",
        "explicame {name}",
        "drivers de {sym}",
        "razones de la caida de {name}",
        "que disparo a {name}",
    ],
    4: [
        "noticias de {name}",
        "ultimas noticias de {sym}",
        "titulares de {name}",
        "news {sym}",
        "novedades de {name}",
        "que dijeron de {name}",
        "que se dijo de {sym} hoy",
    ],
}

HARD_NEG = [
    ("dicen que {name} sube fuerte", 0),  # sin umbral -> no alerta
    ("parece que {name} baja por resultados", 0),
    ("precio de {name} y avisame si baja de {thr}", 2),  # mixta -> alerta
    ("catchate el precio de {name}", 1),
]


def sample_thr():
    return random.choice([50, 100, 150, 200, 250, 300, 500, 1000])


def make_row(t, lab, sym, name):
    txt = t.format(sym=sym, name=name, thr=sample_thr())
    return {"text": txt, "label": lab}


rows = []
pool = list(zip(EQUITIES, NAMES)) + [(c, c.split("-")[0].lower()) for c in CRYPTO]

# Balanced clases
per_class = 220
for lab in [0, 1, 2, 3, 4]:
    for sym, name in pool:
        reps = max(1, per_class // len(pool))
        for _ in range(reps):
            t = random.choice(TEMPLATES[lab])
            rows.append(make_row(t, lab, sym, name))

# Extra variedad por clase
EXTRA_GENERAL = [
    "busca info de {name} en la web",
    "reformula esta consulta: {name} innovacion",
    "que hay sobre {name} en internet",
    "resumen breve sobre {name}",
]
EXTRA_FIN = [
    "cuanto esta {sym}",
    "precio {sym}",
    "precio actual de {name}",
    "cierre de {name}",
]
EXTRA_ALERT = [
    "avisame cuando {sym} cruce {thr}",
    "alerta si {name} perfora {thr}",
    "dispara alerta si {sym} sube de {thr}",
]
EXTRA_EXPLAIN = [
    "que paso con {sym} hoy",
    "{sym} hoy que paso",
    "por que {name} se movio",
    "que motivo la subida de {name}",
    "drivers de {sym} hoy",
]
EXTRA_NEWS = [
    "dame noticias de {sym}",
    "titulares recientes de {name}",
    "ultimas de {sym}",
    "rss de {sym}",
    "headlines {sym}",
]


def _gen_from_templates(templates, label, reps=1):
    for sym, name in pool:
        for _ in range(reps):
            rows.append(make_row(random.choice(templates), label, sym, name))


_gen_from_templates(EXTRA_GENERAL, 0, reps=2)
_gen_from_templates(EXTRA_FIN, 1, reps=2)
_gen_from_templates(EXTRA_ALERT, 2, reps=2)
_gen_from_templates(EXTRA_EXPLAIN, 3, reps=2)
_gen_from_templates(EXTRA_NEWS, 4, reps=2)

# Edge cases
EXTRA_NEG = [
    ("precio y noticias de {sym}", 1),
    ("que pasa con el precio de {name}", 1),
    ("solo quiero titulares de {name}", 4),
    ("por que {name} subio tanto", 3),
    ("por que {name} bajo hoy", 3),
]
for t, lab in EXTRA_NEG:
    for sym, name in random.sample(pool, k=min(6, len(pool))):
        rows.append(make_row(t, lab, sym, name))

for t, lab in HARD_NEG:
    for sym, name in random.sample(pool, k=min(8, len(pool))):
        rows.append(make_row(t, lab, sym, name))

random.shuffle(rows)
rows = rows[:1400]

with open("data/intent.synthetic.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"OK -> data/intent.synthetic.jsonl ({len(rows)} filas)")
