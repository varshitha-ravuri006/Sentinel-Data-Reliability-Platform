from app.core.db import SessionLocal
from app.models.tables import (
    Dataset, ValidationRule, RawRecord, ValidRecord, Quarantine,
)
from app.services.orchestrator import validate_dataset


def test_validate_dataset_sorts_and_stores():
    db = SessionLocal()
    try:
        ds = Dataset(name="orders_test", source_filename="test.csv")
        db.add(ds); db.commit(); db.refresh(ds)

        db.add(ValidationRule(
            dataset_name="orders_test", column_name="customer_id",
            rule_type="not_null", rule_params={},
        ))
        db.add_all([
            RawRecord(dataset_id=ds.id, row_number=0, data={"order_id": "1", "customer_id": "C1"}),
            RawRecord(dataset_id=ds.id, row_number=1, data={"order_id": "2", "customer_id": ""}),
            RawRecord(dataset_id=ds.id, row_number=2, data={"order_id": "3", "customer_id": "C3"}),
        ])
        db.commit()

        summary = validate_dataset(db, ds.id)
        assert summary["total_rows"] == 3
        assert summary["valid"] == 2
        assert summary["invalid"] == 1

        assert db.query(ValidRecord).filter(ValidRecord.dataset_id == ds.id).count() == 2
        assert db.query(Quarantine).filter(Quarantine.dataset_id == ds.id).count() == 1

        db.refresh(ds)
        assert ds.status == "validated"
        assert ds.health_score == 66.67
    finally:
        db.query(RawRecord).filter(RawRecord.dataset_id == ds.id).delete()
        db.query(ValidRecord).filter(ValidRecord.dataset_id == ds.id).delete()
        db.query(Quarantine).filter(Quarantine.dataset_id == ds.id).delete()
        db.query(ValidationRule).filter(ValidationRule.dataset_name == "orders_test").delete()
        db.query(Dataset).filter(Dataset.id == ds.id).delete()
        db.commit(); db.close()
