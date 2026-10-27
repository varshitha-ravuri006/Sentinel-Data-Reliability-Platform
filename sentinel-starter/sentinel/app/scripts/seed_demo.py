"""Seed a demo 'demo_orders' dataset + contract for the demo. Safe to re-run."""
import csv
import io

from app.core.db import SessionLocal
from app.models.tables import Dataset, RawRecord, ValidationRule

NAME = "demo_orders"
CSV = (
    "order_id,customer_id,amount,status\n"
    "1,C1,10,paid\n"
    "2,,20,paid\n"
    "3,C3,-5,paid\n"
    "4,C4,40,unknown\n"
    "5,C5,50,shipped\n"
)
RULES = [
    ("customer_id", "not_null", {}),
    ("amount", "positive", {}),
    ("status", "in_set", {"allowed": ["pending", "paid", "shipped", "cancelled"]}),
]


def main():
    db = SessionLocal()
    try:
        # wipe any earlier demo so re-running doesn't stack duplicates
        for d in db.query(Dataset).filter(Dataset.name == NAME).all():
            db.query(RawRecord).filter(RawRecord.dataset_id == d.id).delete()
            db.delete(d)
        db.query(ValidationRule).filter(ValidationRule.dataset_name == NAME).delete()
        db.commit()

        rows = list(csv.DictReader(io.StringIO(CSV)))
        ds = Dataset(name=NAME, source_filename="demo.csv",
                     total_rows=len(rows), status="uploaded")
        db.add(ds)
        db.commit()
        db.refresh(ds)

        for i, r in enumerate(rows):
            db.add(RawRecord(dataset_id=ds.id, row_number=i, data=dict(r)))
        for col, rt, params in RULES:
            db.add(ValidationRule(dataset_name=NAME, column_name=col,
                                  rule_type=rt, rule_params=params))
        db.commit()
        print(f"Seeded {NAME} with id {ds.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()