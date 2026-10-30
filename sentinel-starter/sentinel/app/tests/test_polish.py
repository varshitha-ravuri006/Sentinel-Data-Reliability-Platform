from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_unknown_dataset_returns_404():
    assert client.get("/datasets/999999/report").status_code == 404
    assert client.get("/datasets/999999/quarantine").status_code == 404
    assert client.post("/datasets/999999/validate").status_code == 404
