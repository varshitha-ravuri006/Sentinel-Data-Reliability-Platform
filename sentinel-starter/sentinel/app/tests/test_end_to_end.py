import io
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal
from app.models.tables import (
    Dataset, ValidationRule, RawRecord, ValidRecord, Quarantine,
)

client = TestClient(app)


def test_full_pipeline():
    name = "e2e_orders"
    csv_data = (
        "order_id,customer_id,amount,status\n"
        "1,C1,10,paid\n"
        "2,,20,paid\n"          # bad: missing customer_id
        "3,C3,-5,paid\n"        # bad: negative amount
        "4,C4,40,unknown\n"     # bad: status not in set
        "5,C5,50,shipped\n"
    )
    files = {"file": ("o.csv", io.BytesIO(csv_data.encode()), "text/csv")}
    up = client.post(f"/datasets/upload?name={name}", files=files)
    dsid = up.json()["dataset_id"]

    for col, rt, params in [
        ("customer_id", "not_null", {}),
        ("amount", "positive", {}),
        ("status", "in_set", {"allowed": ["pending", "paid", "shipped", "cancelled"]}),
    ]:
        client.post("/rules", json={
            "dataset_name": name, "column_name": col,
            "rule_type": rt, "rule_params": params,
        })

    client.post(f"/datasets/{dsid}/validate")
    report = client.get(f"/datasets/{dsid}/report").json()
    assert report["total_rows"] == 5
    assert report["valid"] == 2
    assert report["invalid"] == 3

    # cleanup
    db = SessionLocal()
    try:
        db.query(RawRecord).filter(RawRecord.dataset_id == dsid).delete()
        db.query(ValidRecord).filter(ValidRecord.dataset_id == dsid).delete()
        db.query(Quarantine).filter(Quarantine.dataset_id == dsid).delete()
        db.query(ValidationRule).filter(ValidationRule.dataset_name == name).delete()
        db.query(Dataset).filter(Dataset.id == dsid).delete()
        db.commit()
    finally:
        db.close()