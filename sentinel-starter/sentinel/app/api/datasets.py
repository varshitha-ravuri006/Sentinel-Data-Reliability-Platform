from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.tables import Dataset

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("")
def list_datasets(db: Session = Depends(get_db)):
    rows = db.query(Dataset).all()
    return [
        {"id": d.id, "name": d.name, "status": d.status,
         "total_rows": d.total_rows, "health_score": d.health_score}
        for d in rows
    ]  