from sqlalchemy.orm import Session

from app.models.tables import (
    Dataset, ValidationRule, RawRecord, ValidRecord, Quarantine,
)
from app.schemas.contracts import Rule
from app.services.engine import validate


def validate_dataset(db: Session, dataset_id: int) -> dict:
    # 1. Load the dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset is None:
        raise ValueError(f"Dataset {dataset_id} not found")

    # 2. Load its rules (the data contract) as engine Rule objects
    rule_rows = (
        db.query(ValidationRule)
        .filter(ValidationRule.dataset_name == dataset.name)
        .all()
    )
    rules = [
        Rule(column=r.column_name, rule_type=r.rule_type, params=r.rule_params or {})
        for r in rule_rows
    ]

    # 3. Load the raw rows uploaded for this dataset
    raw_rows = (
        db.query(RawRecord).filter(RawRecord.dataset_id == dataset_id).all()
    )
    rows = [r.data for r in raw_rows]

    # 4. Run the engine (Day 2 code)
    result = validate(rows, rules)

    # 5. Clear previous results so re-running is safe (idempotent)
    db.query(ValidRecord).filter(ValidRecord.dataset_id == dataset_id).delete()
    db.query(Quarantine).filter(Quarantine.dataset_id == dataset_id).delete()

    # 6. Store good rows
    for i, row in enumerate(result.valid_rows):
        db.add(ValidRecord(dataset_id=dataset_id, row_number=i, data=row))

    # 7. Store bad rows with reasons
    for bad in result.invalid_rows:
        db.add(Quarantine(
            dataset_id=dataset_id,
            row_number=bad.row_number,
            data=bad.data,
            failure_reasons=[r.model_dump() for r in bad.reasons],
        ))

    # 8. Update the dataset summary
    dataset.total_rows = result.total_rows
    dataset.valid_rows = result.valid_count
    dataset.invalid_rows = result.invalid_count
    dataset.health_score = result.health_score
    dataset.status = "validated"

    db.commit()
    return {
        "dataset_id": dataset_id,
        "total_rows": result.total_rows,
        "valid": result.valid_count,
        "invalid": result.invalid_count,
        "health_score": result.health_score,
    }

