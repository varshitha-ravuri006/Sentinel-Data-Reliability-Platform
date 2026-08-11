from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import Base, engine, get_db
from app.models import tables  # noqa: F401  (registers models with Base)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Day-1 convenience: create tables on startup.
    # Semester 1 proper: replace with Alembic migrations.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Sentinel", version="0.1.0", lifespan=lifespan)


@app.get("/health", tags=["system"])
def health(db: Session = Depends(get_db)):
    """Liveness + DB connectivity check."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
