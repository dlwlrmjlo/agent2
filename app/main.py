from fastapi import FastAPI
from app.api.endpoints import router as api_router

app = FastAPI(title="Asistente IA Modular")

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "API lista para recibir consultas."}
