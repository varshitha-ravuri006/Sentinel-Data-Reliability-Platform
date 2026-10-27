import csv
import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.tables import Dataset, RawRecord

router = APIRouter(prefix="/datasets", tags=["ingestion"])


@router.post("/upload")
async def upload_dataset(
    name: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 text")

    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        raise HTTPException(status_code=400, detail="CSV has no data rows")

    dataset = Dataset(
        name=name,
        source_filename=file.filename,
        total_rows=len(rows),
        status="uploaded",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    for i, row in enumerate(rows):
        db.add(RawRecord(dataset_id=dataset.id, row_number=i, data=dict(row)))
    db.commit()

    return {"dataset_id": dataset.id, "name": name, "rows_ingested": len(rows)}