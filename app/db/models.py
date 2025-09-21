# app/db/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.database import Base

class Alerta(Base):
    __tablename__ = "alertas"
    id = Column(Integer, primary_key=True, index=True)
    simbolo = Column(String, index=True)
    condicion = Column(String)         # "mayor" | "menor"
    umbral = Column(Float)
    notificado = Column(Boolean, default=False)
