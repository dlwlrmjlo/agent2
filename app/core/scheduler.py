# app/core/scheduler.py
# Poll simple: evalua alertas y notifica por Telegram.

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Alerta
from app.core.market import get_last_price, is_liquid_symbol, is_market_open
from app.core.notifications import enviar_telegram_mensaje
from app.core.config import settings

import asyncio
from app.core.explain import explain_move

def verificar_alertas():
    # ... existing imports ...
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
                
                # --- Alert Triggered: Generate Explanation ---
                msg_base = f"🚨 <b>ALERTA: {a.simbolo}</b>\nCondición: {a.condicion} que {a.umbral}\nPrecio actual: {round(price, 2)}\n\n"
                
                # Run async explain logic synchronously
                try:
                    explanation = asyncio.run(explain_move(a.simbolo))
                    brief = explanation.get("summary_general") or ""
                    
                    # Split logic (Summary /// Details)
                    parts = brief.split("///")
                    if len(parts) > 1:
                        summary_text = parts[0].strip()
                        details_html = parts[1].strip()
                        final_msg = (
                            f"{msg_base}"
                            f"{summary_text}\n\n"
                            f"<tg-spoiler>{details_html}</tg-spoiler>"
                        )
                    else:
                        final_msg = f"{msg_base}{brief.strip()}"
                except Exception as ex:
                    print(f"[alerta] error generando explain: {ex}")
                    final_msg = f"{msg_base}No se pudo generar explicación detallada."

                enviar_telegram_mensaje(final_msg, parse_mode="HTML")
                print(f"[alerta] disparada {a.simbolo}")
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
