import csv
import io

from fastapi import APIRouter, Depends, File, UploadFile
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
    content = await file.read()
    text = content.decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(text)))

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
