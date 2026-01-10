# Intent Eval Report (LLM vs Adapter, 5 clases)

- Items: **1039**

## Resumen de Métricas

| Modo | Accuracy | F1-macro | Lat p50 (ms) | Lat p95 (ms) |
|---|---:|---:|---:|---:|
| LLM | 0.7719 | 0.7707 | 1763 | 2617 |
| Adapter | 0.9923 | 0.9924 | 30 | 55 |

## Matrices de confusión (filas=true, columnas=pred)

**LLM**

```
[193, 8, 0, 12, 0]
[28, 172, 0, 0, 0]
[2, 0, 198, 0, 0]
[105, 29, 0, 78, 1]
[44, 8, 0, 0, 161]
```

**Adapter**

```
[210, 1, 0, 1, 1]
[0, 199, 0, 0, 1]
[0, 0, 200, 0, 0]
[1, 0, 0, 212, 0]
[1, 2, 0, 0, 210]
```

## Mismatches (total 241)

- gold=1 | llm=0 | adp=1 | txt: cierre de netflix
- gold=4 | llm=1 | adp=4 | txt: titulares financieros de btc
- gold=3 | llm=1 | adp=3 | txt: parece que nvidia baja por resultados
- gold=1 | llm=0 | adp=1 | txt: a cuánto está SQM
- gold=3 | llm=0 | adp=3 | txt: drivers de GOOGL hoy
- gold=3 | llm=0 | adp=3 | txt: por qué bajó amazon
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a netflix
- gold=1 | llm=0 | adp=1 | txt: precio de sol
- gold=3 | llm=0 | adp=3 | txt: motivo del rally de GOOGL
- gold=1 | llm=1 | adp=4 | txt: cotización NFLX
- gold=3 | llm=0 | adp=3 | txt: motivo del rally de SOL-USD
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en sol
- gold=3 | llm=0 | adp=3 | txt: por qué se movió tesla
- gold=0 | llm=1 | adp=0 | txt: competidores de amd
- gold=3 | llm=0 | adp=3 | txt: qué pasa con AMZN
- gold=3 | llm=0 | adp=3 | txt: causas de la caída de sol
- gold=3 | llm=0 | adp=3 | txt: parece que sol baja por resultados
- gold=4 | llm=0 | adp=4 | txt: titulares financieros de sqm
- gold=4 | llm=0 | adp=4 | txt: dicen que amazon sube fuerte
- gold=4 | llm=0 | adp=4 | txt: dicen que eth sube fuerte
- gold=4 | llm=0 | adp=4 | txt: titulares de AMD
- gold=4 | llm=0 | adp=4 | txt: titulares de AAPL
- gold=3 | llm=0 | adp=3 | txt: qué pasa con MSFT
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a sol
- gold=3 | llm=0 | adp=3 | txt: qué pasó con amd
- gold=4 | llm=1 | adp=4 | txt: titulares financieros de amd
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a eth
- gold=4 | llm=0 | adp=1 | txt: titulares de ETH-USD
- gold=1 | llm=0 | adp=1 | txt: dame el precio de sol
- gold=1 | llm=0 | adp=1 | txt: acciones de sol
- gold=3 | llm=0 | adp=3 | txt: qué pasó con netflix
- gold=3 | llm=0 | adp=3 | txt: qué pasó con netflix
- gold=3 | llm=0 | adp=3 | txt: qué pasa con MSFT
- gold=1 | llm=0 | adp=1 | txt: ticker de sol
- gold=3 | llm=0 | adp=3 | txt: drivers de GOOGL hoy
- gold=1 | llm=0 | adp=1 | txt: a cuánto está SQM
- gold=0 | llm=0 | adp=3 | txt: crees que apple suba?
- gold=1 | llm=0 | adp=1 | txt: valor de sol
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de nvidia
- gold=3 | llm=0 | adp=3 | txt: por qué se movió eth
- gold=3 | llm=0 | adp=3 | txt: qué pasó con tesla
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de tesla
- gold=0 | llm=1 | adp=0 | txt: competidores de amd
- gold=3 | llm=0 | adp=3 | txt: motivo del rally de META
- gold=3 | llm=1 | adp=3 | txt: análisis del movimiento de amd
- gold=1 | llm=0 | adp=1 | txt: cierre de google
- gold=0 | llm=1 | adp=0 | txt: competidores de eth
- gold=3 | llm=0 | adp=3 | txt: por qué bajó amazon
- gold=0 | llm=3 | adp=0 | txt: crees que sqm suba?
- gold=4 | llm=0 | adp=4 | txt: titulares de AMZN
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de netflix
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a apple
- gold=1 | llm=0 | adp=1 | txt: a cuánto está SQM
- gold=4 | llm=0 | adp=4 | txt: titulares de AMZN
- gold=4 | llm=0 | adp=4 | txt: dicen que nvidia sube fuerte
- gold=0 | llm=1 | adp=0 | txt: competidores de eth
- gold=4 | llm=0 | adp=4 | txt: titulares de AMD
- gold=3 | llm=1 | adp=3 | txt: análisis del movimiento de amd
- gold=3 | llm=0 | adp=3 | txt: drivers de AMZN hoy
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en google
- gold=4 | llm=1 | adp=4 | txt: titulares financieros de btc
- gold=3 | llm=1 | adp=3 | txt: qué pasa con BTC-USD
- gold=3 | llm=0 | adp=3 | txt: por qué subió MSFT
- gold=3 | llm=0 | adp=3 | txt: por qué bajó google
- gold=3 | llm=0 | adp=0 | txt: qué está moviendo a google
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de netflix
- gold=4 | llm=0 | adp=4 | txt: dicen que microsoft sube fuerte
- gold=3 | llm=0 | adp=3 | txt: motivo del rally de NFLX
- gold=3 | llm=1 | adp=3 | txt: parece que btc baja por resultados
- gold=4 | llm=0 | adp=4 | txt: dicen que netflix sube fuerte
- gold=0 | llm=1 | adp=0 | txt: crees que amd suba?
- gold=1 | llm=0 | adp=1 | txt: quote SQM
- gold=3 | llm=0 | adp=3 | txt: drivers de SOL-USD hoy
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de tesla
- gold=0 | llm=1 | adp=0 | txt: crees que nvidia suba?
- gold=3 | llm=0 | adp=3 | txt: por qué bajó btc
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en meta
- gold=0 | llm=1 | adp=0 | txt: crees que tesla suba?
- gold=1 | llm=0 | adp=1 | txt: quote SQM
- gold=3 | llm=0 | adp=3 | txt: qué pasa con MSFT
- gold=4 | llm=0 | adp=4 | txt: prensa sobre sol
- gold=3 | llm=1 | adp=3 | txt: qué está moviendo a eth
- gold=3 | llm=0 | adp=3 | txt: por qué se movió apple
- gold=3 | llm=0 | adp=3 | txt: qué pasó con tesla
- gold=3 | llm=4 | adp=3 | txt: causas de la caída de amazon
- gold=3 | llm=1 | adp=3 | txt: motivo del rally de AMD
- gold=3 | llm=0 | adp=3 | txt: qué pasa con MSFT
- gold=1 | llm=0 | adp=1 | txt: valor de amazon
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a amazon
- gold=1 | llm=0 | adp=1 | txt: cierre de sqm
- gold=1 | llm=0 | adp=1 | txt: cierre de sqm
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a netflix
- gold=3 | llm=1 | adp=3 | txt: por qué bajó nvidia
- gold=3 | llm=1 | adp=3 | txt: por qué subió TSLA
- gold=0 | llm=0 | adp=1 | txt: datos generales de BTC-USD
- gold=3 | llm=0 | adp=3 | txt: por qué subió MSFT
- gold=3 | llm=0 | adp=3 | txt: drivers de NVDA hoy
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de microsoft
- gold=3 | llm=1 | adp=3 | txt: motivo del rally de NVDA
- gold=3 | llm=1 | adp=3 | txt: parece que amd baja por resultados
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de sqm
- gold=0 | llm=1 | adp=0 | txt: análisis fundamental de tesla
- gold=3 | llm=0 | adp=3 | txt: por qué se movió sol
- gold=3 | llm=0 | adp=3 | txt: parece que google baja por resultados
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de amazon
- gold=1 | llm=0 | adp=1 | txt: ticker de sol
- gold=4 | llm=1 | adp=4 | txt: titulares financieros de btc
- gold=4 | llm=0 | adp=4 | txt: titulares de GOOGL
- gold=4 | llm=1 | adp=4 | txt: titulares financieros de apple
- gold=3 | llm=1 | adp=3 | txt: parece que netflix baja por resultados
- gold=4 | llm=0 | adp=4 | txt: dicen que meta sube fuerte
- gold=3 | llm=0 | adp=3 | txt: por qué subió GOOGL
- gold=0 | llm=0 | adp=4 | txt: crees que amazon suba?
- gold=3 | llm=0 | adp=3 | txt: drivers de TSLA hoy
- gold=3 | llm=0 | adp=3 | txt: por qué subió BTC-USD
- gold=4 | llm=0 | adp=4 | txt: titulares de SQM
- gold=3 | llm=0 | adp=3 | txt: drivers de TSLA hoy
- gold=1 | llm=0 | adp=1 | txt: precio sol ahora
- gold=4 | llm=0 | adp=4 | txt: dicen que apple sube fuerte
- gold=4 | llm=1 | adp=4 | txt: titulares financieros de amd
- gold=3 | llm=0 | adp=3 | txt: por qué se movió nvidia
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de microsoft
- gold=4 | llm=0 | adp=4 | txt: titulares de MSFT
- gold=3 | llm=1 | adp=3 | txt: análisis del movimiento de amd
- gold=3 | llm=0 | adp=3 | txt: por qué se movió microsoft
- gold=1 | llm=0 | adp=1 | txt: cierre de btc
- gold=1 | llm=0 | adp=1 | txt: acciones de sqm
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en eth
- gold=4 | llm=0 | adp=4 | txt: prensa sobre tesla
- gold=3 | llm=0 | adp=3 | txt: por qué bajó nvidia
- gold=3 | llm=0 | adp=3 | txt: por qué subió BTC-USD
- gold=1 | llm=0 | adp=1 | txt: cierre de sol
- gold=1 | llm=0 | adp=1 | txt: cierre de microsoft
- gold=3 | llm=0 | adp=3 | txt: qué pasa con NFLX
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en sol
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a amazon
- gold=1 | llm=0 | adp=1 | txt: quote SQM
- gold=3 | llm=0 | adp=3 | txt: motivo del rally de AAPL
- gold=3 | llm=1 | adp=3 | txt: por qué subió AMZN
- gold=1 | llm=0 | adp=1 | txt: acciones de sqm
- gold=3 | llm=0 | adp=3 | txt: motivo del rally de AMZN
- gold=3 | llm=1 | adp=3 | txt: drivers de AMD hoy
- gold=3 | llm=0 | adp=3 | txt: qué pasa con AMD
- gold=2 | llm=0 | adp=2 | txt: cuando amazon rompa 500 me avisas
- gold=4 | llm=0 | adp=4 | txt: titulares financieros de apple
- gold=4 | llm=0 | adp=4 | txt: titulares de TSLA
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de nvidia
- gold=1 | llm=0 | adp=1 | txt: acciones de sqm
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de amazon
- gold=3 | llm=0 | adp=3 | txt: qué pasa con NVDA
- gold=3 | llm=0 | adp=3 | txt: por qué se movió microsoft
- gold=3 | llm=1 | adp=3 | txt: qué pasa con BTC-USD
- gold=3 | llm=0 | adp=3 | txt: qué pasó con google
- gold=3 | llm=0 | adp=3 | txt: por qué bajó eth
- gold=3 | llm=0 | adp=3 | txt: drivers de GOOGL hoy
- gold=3 | llm=0 | adp=3 | txt: drivers de NFLX hoy
- gold=0 | llm=3 | adp=0 | txt: historia de amd
- gold=4 | llm=0 | adp=4 | txt: dicen que google sube fuerte
- gold=3 | llm=0 | adp=3 | txt: por qué subió SOL-USD
- gold=4 | llm=0 | adp=4 | txt: dicen que sol sube fuerte
- gold=3 | llm=0 | adp=3 | txt: por qué subió NFLX
- gold=0 | llm=3 | adp=0 | txt: análisis fundamental de apple
- gold=1 | llm=0 | adp=1 | txt: cierre de nvidia
- gold=4 | llm=0 | adp=4 | txt: titulares financieros de sol
- gold=3 | llm=1 | adp=3 | txt: parece que eth baja por resultados
- gold=3 | llm=1 | adp=3 | txt: motivo del rally de AMD
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de eth
- gold=3 | llm=0 | adp=3 | txt: drivers de NFLX hoy
- gold=3 | llm=0 | adp=3 | txt: drivers de AMZN hoy
- gold=3 | llm=0 | adp=3 | txt: drivers de GOOGL hoy
- gold=3 | llm=0 | adp=3 | txt: por qué subió BTC-USD
- gold=0 | llm=3 | adp=0 | txt: información corporativa de sqm
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de apple
- gold=3 | llm=1 | adp=3 | txt: qué está moviendo a amd
- gold=4 | llm=0 | adp=4 | txt: dicen que sqm sube fuerte
- gold=3 | llm=1 | adp=3 | txt: qué está moviendo a eth
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de google
- gold=3 | llm=0 | adp=3 | txt: drivers de GOOGL hoy
- gold=3 | llm=0 | adp=3 | txt: motivo del rally de AAPL
- gold=1 | llm=0 | adp=1 | txt: cierre de amazon
- gold=3 | llm=0 | adp=3 | txt: qué pasó con sol
- gold=3 | llm=0 | adp=3 | txt: análisis del movimiento de meta
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a sqm
- gold=3 | llm=0 | adp=3 | txt: por qué se movió apple
- gold=4 | llm=0 | adp=4 | txt: titulares de MSFT
- gold=3 | llm=0 | adp=3 | txt: drivers de NVDA hoy
- gold=3 | llm=0 | adp=3 | txt: motivo del rally de AAPL
- gold=3 | llm=0 | adp=3 | txt: qué pasó con microsoft
- gold=3 | llm=0 | adp=3 | txt: drivers de NFLX hoy
- gold=3 | llm=0 | adp=3 | txt: qué está moviendo a nvidia
- gold=4 | llm=0 | adp=4 | txt: titulares financieros de netflix
- gold=3 | llm=1 | adp=3 | txt: qué pasó con eth
- gold=4 | llm=0 | adp=4 | txt: qué hay de nuevo en meta
- gold=4 | llm=0 | adp=4 | txt: titulares de AMZN
- gold=4 | llm=0 | adp=4 | txt: titulares de SQM
- gold=4 | llm=0 | adp=4 | txt: titulares financieros de sol
- gold=4 | llm=1 | adp=4 | txt: titulares financieros de tesla
- gold=3 | llm=0 | adp=3 | txt: parece que meta baja por resultados
- gold=3 | llm=0 | adp=3 | txt: qué pasó con eth
- gold=3 | llm=1 | adp=3 | txt: por qué subió AMD

… y 41 más.
