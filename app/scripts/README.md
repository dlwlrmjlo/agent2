# Flujo de Trabajo de Scripts (Intent Classification)

Este directorio contiene los scripts necesarios para entrenar, evaluar y probar el clasificador de intenciones del Agente Financiero.

El flujo de trabajo está diseñado para ser secuencial:

## 1. Generación de Datos (`data/`)
**Script:** `app/scripts/data/gen_intent.py`
*   **Propósito:** Generar un dataset sintético balanceado para las 5 clases desde cero.
*   **Input:** Templates definidos en el script.
*   **Output:** `data/intent_5classes.jsonl`.
*   **Comando:** `python app/scripts/data/gen_intent.py`

## 2. Entrenamiento (`training/`)
**Script:** `app/scripts/training/train.py`
*   **Propósito:** Entrenar el modelo adaptador (SentenceTransformer + Logistic Regression).
*   **Input:** `data/intent_5classes.jsonl`.
*   **Output:** Artefactos del modelo en `models/intent_adapter/` (`encoder.txt`, `lr.joblib`, etc.).
*   **Comando:** `python app/scripts/training/train.py --train data/intent_5classes.jsonl`

## 3. Evaluación (`training/`)
**Script:** `app/scripts/training/evaluate.py`
*   **Propósito:** Comparar el rendimiento del adaptador contra un LLM (usado como "juez" o baseline) para detectar discrepancias.
*   **Input:** Un dataset de prueba (ej. `data/intent_5classes.jsonl` o uno separado).
*   **Output:** Reporte en Markdown y archivo de discrepancias.
*   **Comando:** `python app/scripts/training/evaluate.py`

## 4. Prueba Unitaria / Debugging (Raíz de scripts)
**Script:** `app/scripts/run_eval_single.py`
*   **Propósito:** Probar una predicción en caliente usando el pipeline completo de la aplicación (que puede incluir lógica híbrida Adaptador + LLM).
*   **Uso:** `python app/scripts/run_eval_single.py "tu frase aquí"`

## Otros
*   `ops/`: Scripts operativos (ej. configuración de webhooks).
