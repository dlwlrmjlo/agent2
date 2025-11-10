from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.schema import PromptRequest
from app.api.services import classify_intent, analizar_web, crear_alerta_from_llm, quote_from_prompt, resolve_ticker_from_prompt
from app.core.news import get_ticker_news
from app.core.explain import explain_move
from app.core.summarize import summarize_drivers
from app.core.telemetry import append_intent_event
from app.core.symbols import resolve_symbol

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/consulta")
async def consulta(data: PromptRequest, db: Session = Depends(get_db)):
    prompt = (data.prompt or "").strip()
    intent = await classify_intent(prompt)
    names = {0:'GENERAL',1:'FINANCIERO',2:'ALERTA',3:'EXPLAIN',4:'NEWS'}
    print(f"[intent] {names.get(intent, 'UNK')} ({intent})")

    append_intent_event(prompt, intent)

    if intent == 1:   # FINANCIERO
        return await quote_from_prompt(prompt)
    if intent == 2:   # ALERTA
        return await crear_alerta_from_llm(prompt, db)
    if intent == 3:   # EXPLAIN
        sym = await resolve_ticker_from_prompt(prompt)
        if not sym:
            return {"error": "No pude resolver el símbolo para explicar el movimiento."}
        return await explain_move(sym)
    if intent == 4:   # NEWS
        sym = await resolve_ticker_from_prompt(prompt)
        if not sym:
            return {"error": "No pude resolver el símbolo para noticias."}
        return {"ticker": sym, "news": get_ticker_news(sym, limit=5)}

    # 0 = GENERAL (fallback web analysis)
    return {"respuesta": await analizar_web(prompt)}

@router.get("/explain/{q}")
async def explain(q: str):
    return await explain_move(q)
@router.get("/debug/alertas")
def listar_alertas(db: Session = Depends(get_db)):
    from app.db.models import Alerta
    rows = db.query(Alerta).all()
    return [{"id": a.id, "simbolo": a.simbolo, "condicion": a.condicion, "umbral": a.umbral, "notificado": a.notificado} for a in rows]

@router.get("/news/{q}")
def news_ticker(q: str):
    return {"ticker": q.upper(), "news": get_ticker_news(q, limit=5)}
