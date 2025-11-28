# app/core/scheduler.py
# Poll simple: evalua alertas y notifica por Telegram.

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Alerta
from app.core.market import get_last_price, is_liquid_symbol, is_market_open
from app.core.notifications import enviar_telegram_mensaje
from app.core.config import settings

def verificar_alertas():
    print('[scheduler] Verificando alertas...')
    db: Session = SessionLocal()
    try:
        for a in db.query(Alerta).filter(Alerta.notificado == False).all():
            try:
                if not is_liquid_symbol(a.simbolo):
                    print(f"[alerta] skip iliquida/OTC: {a.simbolo}")
                    continue
                snap = get_last_price(a.simbolo)
                price = snap.price
                if price is None:
                    print(f"[alerta] precio no disponible: {a.simbolo}")
                    continue
                should = (a.condicion == "mayor" and price > a.umbral) or (
                    a.condicion == "menor" and price < a.umbral
                )
                if not should:
                    continue
                msg = f"{a.simbolo} {a.condicion} que {a.umbral}. Precio: {round(price, 2)}"
                enviar_telegram_mensaje(f"🚨 Alerta: {msg}")
                print(f"[alerta] disparada {msg}")
                a.notificado = True
                db.commit()
            except Exception as e:
                print(f"[alerta] error {a.id} {a.simbolo}: {e}")
    finally:
        db.close()


def iniciar_scheduler():
    s = BackgroundScheduler()
    s.add_job(verificar_alertas, "interval", seconds=settings.SCHED_INTERVAL_S)
    s.start()
    print("[scheduler] iniciado")
