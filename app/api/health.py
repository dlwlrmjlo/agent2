from fastapi import APIRouter
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.scheduler import verificar_alertas
from app.db.database import SessionLocal

router = APIRouter()


@router.get("/health")
async def health():
    status = {"status": "UP"}
    # DB check
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except SQLAlchemyError as e:
        status["status"] = "DEGRADED"
        status["db"] = str(e)
    # scheduler
    status["scheduler_interval_s"] = settings.SCHED_INTERVAL_S
    return status
