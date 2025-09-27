from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.schema import PromptRequest
from app.api.services import classify_intent, analizar_web, crear_alerta_from_llm, quote_from_prompt
from app.core.news import get_ticker_news
from app.core.explain import explain_move
from app.core.summarize import summarize_drivers

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/consulta")
async def consulta(data: PromptRequest, db: Session = Depends(get_db)):
    prompt = (data.prompt or "").strip()
    intent = await classify_intent(prompt)
    print(f"[intent] {['GENERAL','FINANCIERO','ALERTA'][intent]} ({intent})")

    if intent == 1:   # FINANCIERO
        return await quote_from_prompt(prompt)
    if intent == 2:   # ALERTA
        return await crear_alerta_from_llm(prompt, db)

    # GENERAL
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
