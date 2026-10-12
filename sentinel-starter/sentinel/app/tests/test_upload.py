import io

from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal
from app.models.tables import Dataset, RawRecord

client = TestClient(app)


def test_upload_ingests_rows():
    csv_data = "order_id,customer_id\n1,C1\n2,C2\n3,C3\n"
    files = {"file": ("test.csv", io.BytesIO(csv_data.encode()), "text/csv")}
    resp = client.post("/datasets/upload?name=upload_test", files=files)
    assert resp.status_code == 200
    assert resp.json()["rows_ingested"] == 3

    db = SessionLocal()
    try:
        ds = db.query(Dataset).filter(Dataset.name == "upload_test").first()
        assert db.query(RawRecord).filter(RawRecord.dataset_id == ds.id).count() == 3
    finally:
        db.query(RawRecord).filter(RawRecord.dataset_id == ds.id).delete()
        db.query(Dataset).filter(Dataset.id == ds.id).delete()
        db.commit()
        db.close()