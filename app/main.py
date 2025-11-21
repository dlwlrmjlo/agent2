# app/main.py
from fastapi import FastAPI

from app.api.endpoints import router as api_router
from app.api.health import router as health_router
from app.api.location import router as loc_router
from app.api.telegram_webhook import router as tg_router
from app.core.scheduler import iniciar_scheduler
from app.db.database import Base, engine

app = FastAPI(title="Asistente IA Modular")

Base.metadata.create_all(bind=engine)
iniciar_scheduler()

app.include_router(api_router, prefix="/api")
app.include_router(tg_router)
app.include_router(loc_router, prefix="/api", tags=["Ubicación"])
app.include_router(health_router)


@app.get("/")
async def root():
    return {"message": "API lista"}
