from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.orchestrator import validate_dataset

router = APIRouter(prefix="/datasets", tags=["validation"])


@router.post("/{dataset_id}/validate")
def run_validation(dataset_id: int, db: Session = Depends(get_db)):
    try:
        return validate_dataset(db, dataset_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
