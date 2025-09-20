# app/core/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Alerta
import yfinance as yf
from app.core.notifications import enviar_telegram_mensaje
from app.core.market import get_last_price
import time

def verificar_alertas():
    print("⏰ Verificando alertas...")
    db: Session = SessionLocal()
    try:
        alertas = db.query(Alerta).filter(Alerta.notificado == False).all()

        for alerta in alertas:
            try:
                ticker = yf.Ticker(alerta.simbolo)
                precio = get_last_price(alerta.simbolo).price

                if precio is None:
                    print(f"❌ No se pudo obtener el precio de {alerta.simbolo}")
                    continue

                if alerta.condicion == "mayor" and precio > alerta.umbral:
                    print(f"🔔 Alerta: {alerta.simbolo} subió de {alerta.umbral} → Precio actual: {precio}")
                    mensaje = f"🚨 Alerta: {alerta.simbolo} {alerta.condicion} que {alerta.umbral}. Precio actual: {precio}"
                    enviar_telegram_mensaje(mensaje)
                    alerta.notificado = True

                elif alerta.condicion == "menor" and precio < alerta.umbral:
                    print(f"🔔 Alerta: {alerta.simbolo} bajó de {alerta.umbral} → Precio actual: {precio}")
                    mensaje = f"🚨 Alerta: {alerta.simbolo} {alerta.condicion} que {alerta.umbral}. Precio actual: {precio}"
                    enviar_telegram_mensaje(mensaje)
                    alerta.notificado = True

                db.commit()

            except Exception as e:
                print(f"⚠️ Error con {alerta.simbolo}: {str(e)}")
    finally:
        db.close()

def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(verificar_alertas, 'interval', seconds=60)
    scheduler.start()
    print("✅ Scheduler iniciado")
