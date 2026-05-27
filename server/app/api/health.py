from fastapi import APIRouter
from app.db.database import SessionLocal

router = APIRouter()


@router.get("/health")
def health_check():
    """Liveness + readiness probe."""
    db_ok = False
    try:
        db = SessionLocal()
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db.close()
        db_ok = True
    except Exception:
        pass

    return {
        "status": "ok" if db_ok else "degraded",
        "db": "connected" if db_ok else "unavailable",
    }
