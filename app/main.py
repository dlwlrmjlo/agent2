from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.db.database import Base, engine
from app.core.scheduler import iniciar_scheduler

app = FastAPI(title="Asistente IA Modular")

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Iniciar el scheduler
iniciar_scheduler()

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "API lista para recibir consultas."}
