# Intent Eval Report (LLM vs Adapter, 5 clases)

- Items: **1039**

## Resumen de Métricas

| Modo | Accuracy | F1-macro | Lat p50 (ms) | Lat p95 (ms) |
|---|---:|---:|---:|---:|
| LLM | 0.8961 | 0.9023 | 1476 | 2315 |
| Adapter | 0.9923 | 0.9924 | 28 | 37 |

## Matrices de confusión (filas=true, columnas=pred)

**LLM**

```
[203, 0, 0, 10, 0]
[33, 167, 0, 0, 0]
[0, 0, 200, 0, 0]
[38, 0, 0, 175, 0]
[27, 0, 0, 0, 186]
```

**Adapter**

```
[210, 1, 0, 1, 1]
[0, 199, 0, 0, 1]
[0, 0, 200, 0, 0]
[1, 0, 0, 212, 0]
[1, 2, 0, 0, 210]
```

## Mismatches (total 114)

- gold=1 | llm=0 | adp=1 | txt: cierre de netflix
- gold=3 | llm=0 | adp=3 | txt: parece que nvidia baja por resultados
- gold=1 | llm=0 | adp=1 | txt: acciones de amazon
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a netflix
- gold=1 | llm=0 | adp=1 | txt: ticker de sol
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en microsoft
- gold=1 | llm=1 | adp=4 | txt: cotización NFLX
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en sol
- gold=1 | llm=0 | adp=1 | txt: ticker de amd
- gold=1 | llm=0 | adp=1 | txt: acciones de eth
- gold=3 | llm=0 | adp=3 | txt: parece que sol baja por resultados
- gold=4 | llm=0 | adp=4 | txt: dicen que amazon sube fuerte
- gold=4 | llm=0 | adp=4 | txt: dicen que eth sube fuerte
- gold=3 | llm=0 | adp=3 | txt: qué pasa con MSFT
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a sol
- gold=1 | llm=0 | adp=1 | txt: acciones de netflix
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de sqm
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a eth
- gold=4 | llm=4 | adp=1 | txt: titulares de ETH-USD
- gold=1 | llm=0 | adp=1 | txt: ticker de nvidia
- gold=1 | llm=0 | adp=1 | txt: acciones de sol
- gold=3 | llm=0 | adp=3 | txt: qué pasó con netflix
- gold=3 | llm=0 | adp=3 | txt: qué pasa con MSFT
- gold=1 | llm=0 | adp=1 | txt: ticker de btc
- gold=1 | llm=0 | adp=1 | txt: ticker de sol
- gold=0 | llm=0 | adp=3 | txt: crees que apple suba?
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de nvidia
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de microsoft
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de tesla
- gold=1 | llm=0 | adp=1 | txt: acciones de btc
- gold=1 | llm=0 | adp=1 | txt: cierre de google
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a apple
- gold=4 | llm=0 | adp=4 | txt: dicen que nvidia sube fuerte
- gold=1 | llm=0 | adp=1 | txt: ticker de amd
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en google
- gold=1 | llm=0 | adp=1 | txt: ticker de btc
- gold=3 | llm=0 | adp=0 | txt: qué está moviendo a google
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de netflix
- gold=4 | llm=0 | adp=4 | txt: dicen que microsoft sube fuerte
- gold=3 | llm=0 | adp=3 | txt: parece que btc baja por resultados
- gold=4 | llm=0 | adp=4 | txt: dicen que netflix sube fuerte
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de tesla
- gold=1 | llm=0 | adp=1 | txt: ticker de btc
- gold=1 | llm=0 | adp=1 | txt: acciones de google
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en meta
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en netflix
- gold=3 | llm=0 | adp=3 | txt: qué pasa con MSFT
- gold=4 | llm=0 | adp=4 | txt: prensa sobre sol
- gold=3 | llm=0 | adp=3 | txt: qué pasa con MSFT
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a amazon
- gold=1 | llm=0 | adp=1 | txt: cierre de sqm
- gold=0 | llm=0 | adp=1 | txt: datos generales de BTC-USD
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de microsoft
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en microsoft
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de sqm
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de tesla
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de amazon
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en microsoft
- gold=1 | llm=0 | adp=1 | txt: ticker de sol
- gold=1 | llm=0 | adp=1 | txt: acciones de meta
- gold=4 | llm=0 | adp=4 | txt: dicen que meta sube fuerte
- gold=0 | llm=0 | adp=4 | txt: crees que amazon suba?
- gold=4 | llm=0 | adp=4 | txt: dicen que apple sube fuerte
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de microsoft
- gold=1 | llm=0 | adp=1 | txt: acciones de amd
- gold=1 | llm=0 | adp=1 | txt: ticker de amd
- gold=1 | llm=0 | adp=1 | txt: acciones de sqm
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en eth
- gold=1 | llm=0 | adp=1 | txt: cierre de sol
- gold=3 | llm=0 | adp=3 | txt: qué pasa con NFLX
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en sol
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a amazon
- gold=1 | llm=0 | adp=1 | txt: acciones de sqm
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de nvidia
- gold=1 | llm=0 | adp=1 | txt: acciones de sqm
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de amazon
- gold=3 | llm=0 | adp=3 | txt: qué pasó con google
- gold=1 | llm=0 | adp=1 | txt: acciones de nvidia
- gold=4 | llm=0 | adp=4 | txt: dicen que google sube fuerte
- gold=4 | llm=0 | adp=4 | txt: dicen que sol sube fuerte
- gold=3 | llm=0 | adp=3 | txt: parece que eth baja por resultados
- gold=1 | llm=0 | adp=1 | txt: acciones de google
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de eth
- gold=1 | llm=0 | adp=1 | txt: acciones de sqm
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de apple
- gold=4 | llm=0 | adp=4 | txt: dicen que sqm sube fuerte
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a eth
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de google
- gold=3 | llm=0 | adp=3 | txt: qué pasó con sol
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de meta
- gold=3 | llm=0 | adp=3 | txt: qué pasó con microsoft
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a nvidia
- gold=1 | llm=0 | adp=1 | txt: ticker de netflix
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en meta
- gold=1 | llm=0 | adp=1 | txt: acciones de google
- gold=3 | llm=0 | adp=3 | txt: qué pasó con eth
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en google
- gold=3 | llm=0 | adp=3 | txt: parece que amazon baja por resultados
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de nvidia
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en netflix
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de apple
- gold=4 | llm=0 | adp=4 | txt: dicen que btc sube fuerte
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de microsoft
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a eth
- gold=1 | llm=0 | adp=1 | txt: ticker de amazon
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de eth
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de microsoft
- gold=4 | llm=4 | adp=1 | txt: titulares de BTC-USD
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en netflix
- gold=1 | llm=0 | adp=1 | txt: acciones de tesla
- gold=1 | llm=0 | adp=1 | txt: cierre de apple
- gold=4 | llm=0 | adp=0 | txt: dicen que tesla sube fuerte
- gold=4 | llm=0 | adp=4 | txt: dicen que amd sube fuerte
- gold=3 | llm=0 | adp=3 | txt: qué pasa con AAPL
