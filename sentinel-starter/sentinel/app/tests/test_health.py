from fastapi.testclient import TestClient


def test_health_endpoint_shape():
    # Import here so collection doesn't require a live DB.
    from app.main import app

    client = TestClient(app)
    # Note: needs the DB up (run inside `docker compose`), proves wiring works.
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
