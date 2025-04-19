from fastapi import FastAPI
from app.api.endpoints import router as scraping_router

app = FastAPI(title="Asistente IA con Scraping Dinámico")

app.include_router(scraping_router, prefix="/api", tags=["Scraping IA"])

@app.get("/")
async def inicio():
    return {"mensaje": "API en funcionamiento"}
