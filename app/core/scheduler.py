# app/core/scheduler.py
# Poll simple: evalúa alertas y notifica por Telegram.

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Alerta
from app.core.market import get_last_price
from app.core.notifications import enviar_telegram_mensaje
from app.core.config import settings

def verificar_alertas():
    print("⏰ Verificando alertas...")
    db: Session = SessionLocal()
    try:
        for a in db.query(Alerta).filter(Alerta.notificado == False).all():
            try:
                price = get_last_price(a.simbolo).price
                if price is None: 
                    print(f"❌ Precio no disponible: {a.simbolo}"); continue
                should = (a.condicion == "mayor" and price > a.umbral) or (a.condicion == "menor" and price < a.umbral)
                if not should: 
                    continue
                enviar_telegram_mensaje(f"🚨 Alerta: {a.simbolo} {a.condicion} que {a.umbral}. Precio: {round(price,2)}")
                print(f"✅ Alerta {a.id} {a.simbolo} notificada")
                a.notificado = True
                db.commit()
            except Exception as e:
                print(f"⚠️ Error alerta {a.id} {a.simbolo}: {e}")
    finally:
        db.close()

def iniciar_scheduler():
    s = BackgroundScheduler()
    s.add_job(verificar_alertas, "interval", seconds=settings.SCHED_INTERVAL_S)
    s.start()
    print("✅ Scheduler iniciado")
