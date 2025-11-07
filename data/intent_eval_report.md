# Intent Eval Report (LLM vs Adapter)

- Items: **806**

## Resumen de mÃ©tricas

| Modo | Accuracy | F1-macro | Lat p50 (ms) | Lat p95 (ms) |
|---|---:|---:|---:|---:|
| LLM | 0.9739 | 0.9739 | 1869 | 2397 |
| Adapter | 0.9975 | 0.9975 | 19 | 21 |

## Matrices de confusiÃ³n (filas=true, columnas=pred; orden de etiquetas: 0,1,2)

**LLM**

```
[275, 0, 0]
[9, 260, 0]
[4, 8, 250]
```

**Adapter**

```
[273, 2, 0]
[0, 269, 0]
[0, 0, 262]
```

## Mismatches (total 23)

Se listan casos donde LLM y Adapter discrepan **o** donde cualquier modo difiere del label real.

- gold=1 | llm=0 | adp=1 | txt: precio de sol
- gold=1 | llm=0 | adp=1 | txt: precio de sol
- gold=2 | llm=0 | adp=2 | txt: cuando sol rompa 100 me avisas
- gold=2 | llm=0 | adp=2 | txt: cuando sol rompa 50 me avisas
- gold=2 | llm=1 | adp=2 | txt: precio de eth y avísame si baja de 200
- gold=2 | llm=0 | adp=2 | txt: cuando sol rompa 100 me avisas
- gold=1 | llm=0 | adp=1 | txt: cáchate el precio de sqm
- gold=2 | llm=1 | adp=2 | txt: precio de apple y avísame si baja de 150
- gold=1 | llm=0 | adp=1 | txt: precio de sol
- gold=1 | llm=0 | adp=1 | txt: precio de sol
- gold=2 | llm=1 | adp=2 | txt: precio de btc y avísame si baja de 100
- gold=2 | llm=1 | adp=2 | txt: precio de google y avísame si baja de 200
- gold=1 | llm=0 | adp=1 | txt: precio de sol
- gold=1 | llm=0 | adp=1 | txt: cáchate el precio de sol
- gold=2 | llm=1 | adp=2 | txt: precio de netflix y avísame si baja de 250
- gold=2 | llm=1 | adp=2 | txt: precio de amd y avísame si baja de 500
- gold=1 | llm=0 | adp=1 | txt: cáchate el precio de google
- gold=2 | llm=0 | adp=2 | txt: cuando netflix rompa 50 me avisas
- gold=2 | llm=1 | adp=2 | txt: precio de sol y avísame si baja de 100
- gold=2 | llm=1 | adp=2 | txt: precio de tesla y avísame si baja de 250
- gold=0 | llm=0 | adp=1 | txt: amd
- gold=1 | llm=0 | adp=1 | txt: dame disney
- gold=0 | llm=0 | adp=1 | txt: dame disney
