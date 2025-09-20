# app/api/location.py
from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Modelo Pydantic de entrada
class UbicacionPayload(BaseModel):
    ubicacion: str  # Ej: "casa", "universidad", "otro"

@router.post("/ubicacion")
async def recibir_ubicacion(data: UbicacionPayload):
    ubicacion = data.ubicacion.strip().lower()
    hora = datetime.now().strftime("%H:%M")

    print(f"📍 Ubicación actual: {ubicacion} (a las {hora})")

    # Aquí puedes activar lógica condicional basada en la ubicación
    if ubicacion == "universidad":
        mensaje = "Estás en la universidad. ¿Quieres estudiar o repasar algo?"
    elif ubicacion == "casa":
        mensaje = "Estás en casa. Es un buen momento para avanzar con tus tareas."
    else:
        mensaje = f"Ubicación detectada: {ubicacion}. ¿Necesitas reorganizar tu día?"

    return {"respuesta": mensaje}
