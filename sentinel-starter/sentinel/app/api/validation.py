from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.orchestrator import validate_dataset
from app.models.tables import Dataset, Quarantine

router = APIRouter(prefix="/datasets", tags=["validation"])


@router.post("/{dataset_id}/validate")
def run_validation(dataset_id: int, db: Session = Depends(get_db)):
    try:
        return validate_dataset(db, dataset_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{dataset_id}/report")
def report(dataset_id: int, db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if ds is None:
        raise HTTPException(status_code=404, detail="dataset not found")

    quarantined = db.query(Quarantine).filter(
        Quarantine.dataset_id == dataset_id).all()
    counter: dict = {}
    for q in quarantined:
        for reason in q.failure_reasons:
            key = f"{reason['column']} · {reason['rule_type']}"
            counter[key] = counter.get(key, 0) + 1
    most_common = max(counter, key=counter.get) if counter else None

    return {
        "dataset": ds.name, "total_rows": ds.total_rows,
        "valid": ds.valid_rows, "invalid": ds.invalid_rows,
        "health_score": ds.health_score, "status": ds.status,
        "most_common_error": most_common,
    }


@router.get("/{dataset_id}/quarantine")
def quarantine(dataset_id: int, limit: int = 50, offset: int = 0,
               db: Session = Depends(get_db)):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if ds is None:
        raise HTTPException(status_code=404, detail="dataset not found")

    rows = (db.query(Quarantine)
            .filter(Quarantine.dataset_id == dataset_id)
            .order_by(Quarantine.row_number)
            .offset(offset).limit(limit).all())
    return [
        {"row_number": r.row_number, "data": r.data, "reasons": r.failure_reasons}
        for r in rows
    ]
