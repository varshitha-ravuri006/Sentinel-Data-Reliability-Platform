from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.datasets import router as datasets_router
from app.api.rules import router as rules_router
from app.api.upload import router as upload_router
from app.api.validation import router as validation_router
from app.core.db import Base, engine, get_db
from app.models import tables  # noqa: F401  (registers models with Base)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Day-1 convenience: create tables on startup.
    # Semester 1 proper: replace with Alembic migrations.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Sentinel", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_methods=["*"], allow_headers=["*"],
)
app.include_router(validation_router)
app.include_router(rules_router)
app.include_router(upload_router)
app.include_router(datasets_router)
app.mount("/ui", StaticFiles(directory="static", html=True), name="ui")


@app.get("/health", tags=["system"])
def health(db: Session = Depends(get_db)):
    """Liveness + DB connectivity check."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}