from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal
from app.models.tables import (
    Dataset, RawRecord, ValidRecord, Quarantine, ValidationRule,
)
from app.scripts.generate_data import generate

client = TestClient(app)


def test_generated_csv_has_known_bad_count(tmp_path):
    path = tmp_path / "gen.csv"
    n_bad = generate(str(path), n=100, corrupt_ratio=0.2)
    name = "gen_test"
    dsid = None
    try:
        with open(path, "rb") as f:
            up = client.post(
                f"/datasets/upload?name={name}",
                files={"file": ("gen.csv", f, "text/csv")},
            )
        dsid = up.json()["dataset_id"]

        for col, rt, params in [
            ("customer_id", "not_null", {}),
            ("amount", "positive", {}),
            ("status", "in_set",
             {"allowed": ["pending", "paid", "shipped", "cancelled"]}),
        ]:
            client.post("/rules", json={
                "dataset_name": name, "column_name": col,
                "rule_type": rt, "rule_params": params,
            })

        client.post(f"/datasets/{dsid}/validate")
        report = client.get(f"/datasets/{dsid}/report").json()
        assert report["total_rows"] == 100
        assert report["invalid"] == n_bad
        assert report["valid"] == 100 - n_bad
    finally:
        db = SessionLocal()
        try:
            if dsid:
                db.query(RawRecord).filter(RawRecord.dataset_id == dsid).delete()
                db.query(ValidRecord).filter(ValidRecord.dataset_id == dsid).delete()
                db.query(Quarantine).filter(Quarantine.dataset_id == dsid).delete()
                db.query(Dataset).filter(Dataset.id == dsid).delete()
            db.query(ValidationRule).filter(ValidationRule.dataset_name == name).delete()
            db.commit()
        finally:
            db.close()