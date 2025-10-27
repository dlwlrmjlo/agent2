# Intent Eval Report (LLM vs Adapter)

- Items: **48**

## Resumen de métricas

| Modo | Accuracy | F1-macro | Lat p50 (ms) | Lat p95 (ms) |
|---|---:|---:|---:|---:|
| LLM | 0.9583 | 0.9582 | 1836 | 2198 |
| Adapter | 0.9792 | 0.9791 | 25 | 30 |

## Matrices de confusión (filas=true, columnas=pred; orden de etiquetas: 0,1,2)

**LLM**

```
[16, 0, 0]
[2, 14, 0]
[0, 0, 16]
```

**Adapter**

```
[15, 1, 0]
[0, 16, 0]
[0, 0, 16]
```

## Mismatches (total 3)

Se listan casos donde LLM y Adapter discrepan **o** donde cualquier modo difiere del label real.

- gold=0 | llm=0 | adp=1 | txt: ¿hubo earnings de AMD?
- gold=1 | llm=0 | adp=1 | txt: dame AMD
- gold=1 | llm=0 | adp=1 | txt: valor de sol
