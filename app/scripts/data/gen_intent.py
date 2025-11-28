#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[STEP 1: DATA GENERATION]
Genera un dataset sintético balanceado para las 5 clases de intención.
Output: data/intent_5classes.jsonl

Uso:
  python app/scripts/data/gen_intent.py
"""
import json, os, random

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
os.makedirs("data", exist_ok=True)

# Entidades
EQUITIES = ["TSLA","GOOGL","AAPL","MSFT","NVDA","AMZN","META","AMD","NFLX","SQM"]
NAMES = ["tesla","google","apple","microsoft","nvidia","amazon","meta","amd","netflix","sqm"]
CRYPTO = ["BTC-USD","ETH-USD","SOL-USD"]

# Templates por clase
TEMPLATES = {
    # 0: GENERAL (Contexto amplio, saludos, preguntas fuera de dominio, o sobre la empresa sin pedir precio/news explícito)
    0: [
        "quién es el ceo de {name}",
        "dónde queda la sede de {name}",
        "historia de {name}",
        "a qué se dedica {name}",
        "competidores de {name}",
        "sector de {name}",
        "cuántos empleados tiene {name}",
        "análisis fundamental de {name}",
        "perfil de la empresa {name}",
        "resumen de {name}",
        "información corporativa de {name}",
        "datos generales de {sym}",
        "hola",
        "buenos días",
        "ayuda",
        "qué puedes hacer",
    ],
    # 1: FINANCIERO (Precio, cotización, valor)
    1: [
        "precio de {name}",
        "cotización {sym}",
        "cuánto vale {name} hoy",
        "precio {name} ahora",
        "quote {sym}",
        "valor de {name}",
        "a cuánto está {sym}",
        "dame el precio de {name}",
        "ticker de {name}",
        "acciones de {name}",
        "{sym} price",
        "precio actual de {name}",
        "cierre de {name}",
    ],
    # 2: ALERTA (Reglas con condición y umbral)
    2: [
        "avísame si {name} cae de {thr}",
        "alerta cuando {sym} supere {thr}",
        "notificar si {name} baja de {thr}",
        "si {sym} sube de {thr}, avísame",
        "cuando {name} rompa {thr} me avisas",
        "avisame cuando {sym} cruce {thr}",
        "alerta si {name} perfora {thr}",
        "crear alerta para {sym} mayor a {thr}",
        "notifícame si {name} llega a {thr}",
        "aviso precio {name} < {thr}",
    ],
    # 3: EXPLAIN (Por qué, causas, drivers, explicaciones de movimiento)
    3: [
        "qué pasó con {name}",
        "por qué se movió {name}",
        "explica el movimiento de {name}",
        "por qué bajó {name}",
        "por qué subió {sym}",
        "causas de la caída de {name}",
        "drivers de {sym} hoy",
        "qué está moviendo a {name}",
        "explicación subida {sym}",
        "análisis del movimiento de {name}",
        "motivo del rally de {sym}",
        "por qué se desplomó {name}",
        "qué pasa con {sym}",
    ],
    # 4: NEWS (Noticias, titulares, prensa)
    4: [
        "noticias de {name}",
        "titulares de {sym}",
        "últimas noticias {name}",
        "news {sym}",
        "prensa sobre {name}",
        "qué se dice de {sym} en las noticias",
        "novedades de {name}",
        "artículos recientes de {sym}",
        "buscar noticias de {name}",
        "resumen de noticias {sym}",
        "titulares financieros de {name}",
        "qué hay de nuevo en {name}",
    ]
}

def sample_thr():
    return random.choice([50, 100, 150, 200, 250, 300, 500, 1000])

def make_row(t, lab, sym, name):
    txt = t.format(sym=sym, name=name, thr=sample_thr())
    return {"text": txt, "label": lab}

def generate():
    rows = []
    pool = list(zip(EQUITIES, NAMES)) + [(c, c.split("-")[0].lower()) for c in CRYPTO]
    
    # Generar ~200 ejemplos por clase
    SAMPLES_PER_CLASS = 200
    
    for label, templates in TEMPLATES.items():
        count = 0
        while count < SAMPLES_PER_CLASS:
            sym, name = random.choice(pool)
            tmpl = random.choice(templates)
            rows.append(make_row(tmpl, label, sym, name))
            count += 1
            
    # Casos difíciles (Hard Negatives)
    # Frases que parecen alertas pero son general/news
    hard_negatives = [
        ("dicen que {name} sube fuerte", 4), # Es noticia/rumor, no alerta
        ("parece que {name} baja por resultados", 3), # Es explicación
        ("crees que {name} suba?", 0), # Pregunta general
    ]
    
    for tmpl, label in hard_negatives:
        for sym, name in pool:
            rows.append(make_row(tmpl, label, sym, name))

    random.shuffle(rows)
    return rows

if __name__ == "__main__":
    data = generate()
    out_path = "data/intent_5classes.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for r in data:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    print(f"Generado {out_path} con {len(data)} ejemplos.")
