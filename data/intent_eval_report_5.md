# Intent Eval Report (LLM vs Adapter, 5 clases)

- Items: **794**

## Resumen de Métricas

| Modo | Accuracy | F1-macro | Lat p50 (ms) | Lat p95 (ms) |
|---|---:|---:|---:|---:|
| LLM | 0.7469 | 0.6991 | 1533 | 2349 |
| Adapter | 0.9194 | 0.8963 | 25 | 35 |

## Matrices de confusión (filas=true, columnas=pred)

**LLM**

```
[70, 9, 0, 99, 51]
[5, 132, 0, 0, 0]
[0, 14, 272, 1, 0]
[19, 0, 0, 62, 0]
[3, 0, 0, 0, 57]
```

**Adapter**

```
[171, 8, 0, 16, 34]
[1, 136, 0, 0, 0]
[0, 4, 283, 0, 0]
[1, 0, 0, 80, 0]
[0, 0, 0, 0, 60]
```

## Mismatches (total 209)

- gold=1 | llm=0 | adp=1 | txt: dame disney
- gold=1 | llm=0 | adp=1 | txt: cierre de meta
- gold=1 | llm=0 | adp=1 | txt: cierre de netflix
- gold=1 | llm=0 | adp=1 | txt: cierre de sol
- gold=1 | llm=0 | adp=1 | txt: cierre de google
- gold=1 | llm=1 | adp=0 | txt: cuanto est�� GOOGL
- gold=2 | llm=1 | adp=2 | txt: avísame si sol cae de 150
- gold=2 | llm=1 | adp=1 | txt: precio de apple y avísame si baja de 150
- gold=2 | llm=1 | adp=2 | txt: precio de btc y avísame si baja de 100
- gold=2 | llm=1 | adp=2 | txt: precio de google y avísame si baja de 200
- gold=2 | llm=1 | adp=2 | txt: si NVDA sube de 100, avísame
- gold=2 | llm=3 | adp=2 | txt: notificar si nvidia baja de 300
- gold=2 | llm=1 | adp=2 | txt: precio de netflix y avísame si baja de 250
- gold=2 | llm=1 | adp=1 | txt: precio de amd y avísame si baja de 500
- gold=2 | llm=1 | adp=2 | txt: precio de sol y avísame si baja de 100
- gold=2 | llm=1 | adp=2 | txt: precio de tesla y avísame si baja de 250
- gold=2 | llm=1 | adp=2 | txt: precio de tesla y avísame si baja de 50
- gold=2 | llm=1 | adp=2 | txt: precio de sqm y avísame si baja de 100
- gold=2 | llm=1 | adp=2 | txt: precio de netflix y avísame si baja de 200
- gold=2 | llm=1 | adp=1 | txt: precio de eth y avísame si baja de 150
- gold=2 | llm=1 | adp=1 | txt: precio de apple y avísame si baja de 300
- gold=0 | llm=4 | adp=0 | txt: qué se dice de SQM en las noticias
- gold=0 | llm=3 | adp=0 | txt: explica el movimiento de sqm
- gold=0 | llm=3 | adp=0 | txt: por qué se movió netflix
- gold=0 | llm=3 | adp=0 | txt: por qué se movió amd
- gold=0 | llm=3 | adp=0 | txt: qué pasó con meta
- gold=0 | llm=3 | adp=0 | txt: por qué se movió amazon
- gold=0 | llm=3 | adp=0 | txt: explica el movimiento de btc
- gold=0 | llm=4 | adp=0 | txt: últimas novedades de AMD
- gold=0 | llm=4 | adp=0 | txt: últimas novedades de AAPL
- gold=0 | llm=4 | adp=0 | txt: qué se dice de AAPL en las noticias
- gold=0 | llm=3 | adp=0 | txt: qué pasó con microsoft
- gold=0 | llm=3 | adp=0 | txt: qué pasó con netflix
- gold=0 | llm=4 | adp=0 | txt: últimas novedades de NFLX
- gold=0 | llm=3 | adp=0 | txt: por qué se movió apple
- gold=0 | llm=3 | adp=0 | txt: por qué se movió btc
- gold=0 | llm=3 | adp=0 | txt: por qué se movió eth
- gold=0 | llm=4 | adp=0 | txt: qué se dice de BTC-USD en las noticias
- gold=0 | llm=3 | adp=0 | txt: explica el movimiento de eth
- gold=0 | llm=4 | adp=0 | txt: últimas novedades de GOOGL
- gold=0 | llm=3 | adp=0 | txt: parece que meta baja por resultados
- gold=0 | llm=4 | adp=0 | txt: últimas novedades de META
- gold=0 | llm=4 | adp=4 | txt: últimas novedades de TSLA
- gold=0 | llm=4 | adp=0 | txt: qué se dice de AMD en las noticias
- gold=0 | llm=3 | adp=0 | txt: por qué se movió tesla
- gold=0 | llm=3 | adp=0 | txt: por qué se movió meta
- gold=0 | llm=3 | adp=0 | txt: qué pasó con tesla
- gold=0 | llm=4 | adp=4 | txt: qué se dice de AMZN en las noticias
- gold=0 | llm=3 | adp=0 | txt: parece que eth baja por resultados
- gold=0 | llm=4 | adp=0 | txt: qué se dice de META en las noticias
- gold=0 | llm=4 | adp=0 | txt: qué se dice de GOOGL en las noticias
- gold=0 | llm=4 | adp=4 | txt: últimas novedades de MSFT
- gold=0 | llm=3 | adp=0 | txt: qué pasó con nvidia
- gold=0 | llm=4 | adp=4 | txt: últimas novedades de AMZN
- gold=0 | llm=3 | adp=0 | txt: qué pasó con amd
- gold=0 | llm=3 | adp=0 | txt: explica el movimiento de sol
- gold=0 | llm=3 | adp=0 | txt: qué pasó con sqm
- gold=0 | llm=4 | adp=0 | txt: qué se dice de MSFT en las noticias
- gold=0 | llm=3 | adp=0 | txt: explica el movimiento de google
- gold=0 | llm=3 | adp=0 | txt: explica el movimiento de apple
- gold=0 | llm=3 | adp=0 | txt: explica el movimiento de meta
- gold=0 | llm=3 | adp=0 | txt: por qué se movió nvidia
- gold=0 | llm=3 | adp=0 | txt: por qué se movió google
- gold=0 | llm=3 | adp=0 | txt: explica el movimiento de amazon
- gold=0 | llm=3 | adp=0 | txt: explica el movimiento de microsoft
- gold=0 | llm=4 | adp=0 | txt: qué se dice de NFLX en las noticias
- gold=0 | llm=4 | adp=4 | txt: qué se dice de ETH-USD en las noticias
- gold=0 | llm=4 | adp=4 | txt: últimas novedades de ETH-USD
- gold=0 | llm=4 | adp=4 | txt: últimas novedades de NVDA
- gold=0 | llm=4 | adp=0 | txt: últimas novedades de SOL-USD
- gold=0 | llm=3 | adp=0 | txt: por qué se movió sqm
- gold=0 | llm=3 | adp=0 | txt: parece que netflix baja por resultados
- gold=0 | llm=4 | adp=0 | txt: últimas novedades de SQM
- gold=0 | llm=3 | adp=0 | txt: por qué se movió sol
- gold=0 | llm=4 | adp=0 | txt: últimas novedades de BTC-USD
- gold=0 | llm=3 | adp=0 | txt: explica el movimiento de amd
- gold=0 | llm=3 | adp=0 | txt: explica el movimiento de tesla
- gold=0 | llm=4 | adp=4 | txt: qué se dice de NVDA en las noticias
- gold=0 | llm=3 | adp=0 | txt: parece que tesla baja por resultados
- gold=0 | llm=3 | adp=0 | txt: por qué se movió microsoft
- gold=0 | llm=3 | adp=0 | txt: qué pasó con eth
- gold=0 | llm=4 | adp=4 | txt: qué se dice de TSLA en las noticias
- gold=0 | llm=3 | adp=0 | txt: explica el movimiento de nvidia
- gold=0 | llm=3 | adp=0 | txt: explica el movimiento de netflix
- gold=0 | llm=3 | adp=0 | txt: parece que microsoft baja por resultados
- gold=0 | llm=0 | adp=3 | txt: amd
- gold=0 | llm=3 | adp=3 | txt: Explicame ald
- gold=0 | llm=3 | adp=3 | txt: Que paso con amd
- gold=0 | llm=4 | adp=4 | txt: Noticias de AMD
- gold=0 | llm=4 | adp=4 | txt: News de amd
- gold=0 | llm=4 | adp=4 | txt: novedades de amd
- gold=0 | llm=4 | adp=4 | txt: titulares recientes de eth
- gold=0 | llm=3 | adp=0 | txt: por que cay�� microsoft
- gold=0 | llm=4 | adp=4 | txt: news GOOGL
- gold=0 | llm=3 | adp=0 | txt: expl��came tesla
- gold=0 | llm=1 | adp=0 | txt: ��ltimas de GOOGL
- gold=0 | llm=1 | adp=1 | txt: ��ltimas de ETH-USD
- gold=0 | llm=4 | adp=4 | txt: news ETH-USD
- gold=0 | llm=3 | adp=0 | txt: por que cay�� nvidia
- gold=0 | llm=3 | adp=3 | txt: por qu�� se movi�� amd
- gold=0 | llm=4 | adp=4 | txt: titulares recientes de amazon
- gold=0 | llm=4 | adp=4 | txt: noticias de google
- gold=0 | llm=4 | adp=4 | txt: titulares de btc
- gold=0 | llm=3 | adp=0 | txt: expl��came sqm
- gold=0 | llm=3 | adp=0 | txt: expl��came amazon
- gold=0 | llm=4 | adp=4 | txt: titulares de nvidia
- gold=0 | llm=3 | adp=3 | txt: drivers de NFLX
- gold=0 | llm=4 | adp=4 | txt: novedades de microsoft
- gold=0 | llm=3 | adp=0 | txt: qu�� motiv�� la suba de eth
- gold=0 | llm=1 | adp=0 | txt: ��ltimas de AMD
- gold=0 | llm=3 | adp=0 | txt: por qu�� amazon subi�� tanto
- gold=0 | llm=3 | adp=0 | txt: por qu�� se movi�� google
- gold=0 | llm=3 | adp=0 | txt: qu�� motiv�� la suba de meta
- gold=0 | llm=3 | adp=0 | txt: razones de la ca��da de google
- gold=0 | llm=3 | adp=0 | txt: expl��came google
- gold=0 | llm=4 | adp=4 | txt: news BTC-USD
- gold=0 | llm=0 | adp=3 | txt: AMZN hoy
- gold=0 | llm=4 | adp=4 | txt: dame noticias de NFLX
- gold=0 | llm=4 | adp=4 | txt: dame noticias de GOOGL
- gold=0 | llm=3 | adp=0 | txt: qu�� movi�� a sqm hoy
- gold=0 | llm=0 | adp=1 | txt: ��ltimas de MSFT
- gold=0 | llm=3 | adp=0 | txt: expl��came eth
- gold=0 | llm=3 | adp=3 | txt: por qu�� subi�� tesla
- gold=0 | llm=3 | adp=0 | txt: por que cay�� btc
- gold=0 | llm=3 | adp=0 | txt: razones de la ca��da de sqm
- gold=0 | llm=3 | adp=0 | txt: razones de la ca��da de amd
- gold=0 | llm=1 | adp=0 | txt: ETH-USD hoy, qu�� pas��
- gold=0 | llm=3 | adp=0 | txt: razones de la ca��da de tesla
- gold=0 | llm=3 | adp=0 | txt: por que cay�� sol
- gold=0 | llm=4 | adp=4 | txt: noticias de sqm
- gold=0 | llm=3 | adp=3 | txt: por qu�� se movi�� eth
- gold=0 | llm=1 | adp=1 | txt: ��ltimas de SQM
- gold=0 | llm=0 | adp=1 | txt: ETH-USD hoy
- gold=0 | llm=3 | adp=0 | txt: por que cay�� eth
- gold=0 | llm=3 | adp=0 | txt: razones de la ca��da de nvidia
- gold=0 | llm=4 | adp=4 | txt: noticias de sol
- gold=0 | llm=4 | adp=4 | txt: noticias de amazon
- gold=0 | llm=3 | adp=3 | txt: drivers de AAPL
- gold=0 | llm=3 | adp=3 | txt: por qu�� subi�� btc
- gold=0 | llm=4 | adp=0 | txt: qu�� dijeron de sqm
- gold=0 | llm=4 | adp=4 | txt: ��ltimas noticias de NFLX
- gold=0 | llm=3 | adp=3 | txt: por que cay�� tesla
- gold=0 | llm=3 | adp=0 | txt: por qu�� google subi�� tanto
- gold=0 | llm=3 | adp=0 | txt: AMD hoy, qu�� pas��
- gold=0 | llm=1 | adp=1 | txt: qu�� pasa con el precio de netflix
- gold=0 | llm=3 | adp=0 | txt: por qu�� subi�� nvidia
- gold=0 | llm=3 | adp=0 | txt: por qu�� se movi�� netflix
- gold=0 | llm=3 | adp=0 | txt: por qu�� apple baj�� hoy
- gold=0 | llm=0 | adp=3 | txt: meta hoy
- gold=0 | llm=3 | adp=3 | txt: por qu�� subi�� eth
- gold=0 | llm=3 | adp=0 | txt: expl��came btc
- gold=0 | llm=3 | adp=0 | txt: expl��came meta
- gold=0 | llm=3 | adp=0 | txt: expl��came microsoft
- gold=0 | llm=3 | adp=0 | txt: qu�� motiv�� la suba de tesla
- gold=0 | llm=3 | adp=0 | txt: por qu�� sqm baj�� hoy
- gold=0 | llm=3 | adp=0 | txt: parece que apple baja por resultados
- gold=0 | llm=3 | adp=3 | txt: explain META
- gold=0 | llm=3 | adp=0 | txt: razones de la ca��da de eth
- gold=0 | llm=3 | adp=3 | txt: por que cay�� amd
- gold=0 | llm=3 | adp=3 | txt: explain MSFT
- gold=0 | llm=4 | adp=0 | txt: novedades de sqm
- gold=0 | llm=4 | adp=4 | txt: ��ltimas noticias de META
- gold=0 | llm=3 | adp=0 | txt: qu�� motiv�� la suba de apple
- gold=0 | llm=3 | adp=0 | txt: qu�� motiv�� la suba de btc
- gold=0 | llm=0 | adp=4 | txt: qu�� dijeron de btc
- gold=0 | llm=3 | adp=0 | txt: expl��came apple
- gold=0 | llm=4 | adp=4 | txt: novedades de google
- gold=0 | llm=3 | adp=0 | txt: por que cay�� meta
- gold=0 | llm=4 | adp=4 | txt: qu�� dijeron de netflix
- gold=0 | llm=1 | adp=1 | txt: SOL-USD hoy
- gold=0 | llm=4 | adp=4 | txt: qu�� dijeron de apple
- gold=0 | llm=3 | adp=0 | txt: qu�� motiv�� la suba de sqm
- gold=0 | llm=4 | adp=4 | txt: titulares recientes de google
- gold=0 | llm=4 | adp=4 | txt: dame noticias de AMD
- gold=0 | llm=3 | adp=0 | txt: qu�� motiv�� la suba de microsoft
- gold=0 | llm=3 | adp=0 | txt: por qu�� apple subi�� tanto
- gold=0 | llm=3 | adp=0 | txt: expl��came netflix
- gold=0 | llm=3 | adp=0 | txt: por qu�� se movi�� sqm
- gold=0 | llm=3 | adp=0 | txt: por qu�� microsoft subi�� tanto
- gold=0 | llm=1 | adp=1 | txt: qu�� pasa con el precio de nvidia
- gold=0 | llm=3 | adp=0 | txt: por qu�� meta baj�� hoy
- gold=0 | llm=1 | adp=1 | txt: qu�� pasa con el precio de google
- gold=0 | llm=3 | adp=0 | txt: explain NFLX
- gold=0 | llm=3 | adp=0 | txt: por qu�� btc subi�� tanto
- gold=0 | llm=3 | adp=0 | txt: explain GOOGL
- gold=0 | llm=3 | adp=0 | txt: por que cay�� google
- gold=3 | llm=0 | adp=3 | txt: que paso con BTC-USD hoy
- gold=3 | llm=0 | adp=3 | txt: que paso con amazon
- gold=3 | llm=0 | adp=3 | txt: que paso con apple
- gold=3 | llm=0 | adp=3 | txt: que paso con AMD hoy
- gold=3 | llm=0 | adp=3 | txt: por que se movio sol
- gold=3 | llm=3 | adp=0 | txt: por que subio nvidia
- gold=3 | llm=0 | adp=3 | txt: que paso con MSFT hoy
- gold=3 | llm=0 | adp=3 | txt: que paso con GOOGL hoy
- gold=3 | llm=0 | adp=3 | txt: que paso con google
- gold=3 | llm=0 | adp=3 | txt: que paso con netflix
- gold=3 | llm=0 | adp=3 | txt: que paso con NVDA hoy
- gold=3 | llm=0 | adp=3 | txt: que paso con META hoy
- gold=3 | llm=0 | adp=3 | txt: que paso con ETH-USD hoy
- gold=3 | llm=0 | adp=3 | txt: que paso con meta

… y 9 más.
