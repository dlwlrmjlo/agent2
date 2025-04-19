from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.database import Base

class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    simbolo = Column(String, index=True)  # Ej: BTC, AAPL, NVDA
    condicion = Column(String)            # "mayor" o "menor"
    umbral = Column(Float)                # Ej: 30000.00
    notificado = Column(Boolean, default=False)
