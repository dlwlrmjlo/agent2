from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str

class AlertaCreate(BaseModel):
    simbolo: str
    condicion: str  # "mayor" o "menor"
    umbral: float