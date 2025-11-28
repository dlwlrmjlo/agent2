# Intent Eval Report (LLM vs Adapter, 5 clases)

- Items: **20**

## Resumen de Métricas

| Modo | Accuracy | F1-macro | Lat p50 (ms) | Lat p95 (ms) |
|---|---:|---:|---:|---:|
| LLM | 1.0000 | 1.0000 | 1234 | 2385 |
| Adapter | 1.0000 | 1.0000 | 26 | 227 |

## Matrices de confusión (filas=true, columnas=pred)

**LLM**

```
[7, 0, 0, 0, 0]
[0, 4, 0, 0, 0]
[0, 0, 4, 0, 0]
[0, 0, 0, 1, 0]
[0, 0, 0, 0, 4]
```

**Adapter**

```
[7, 0, 0, 0, 0]
[0, 4, 0, 0, 0]
[0, 0, 4, 0, 0]
[0, 0, 0, 1, 0]
[0, 0, 0, 0, 4]
```

## Mismatches (total 0)

