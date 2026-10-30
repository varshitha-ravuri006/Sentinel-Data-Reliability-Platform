from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal
from app.models.tables import ValidationRule

client = TestClient(app)
NAME = "rules_api_test"


def _cleanup():
    db = SessionLocal()
    try:
        db.query(ValidationRule).filter(ValidationRule.dataset_name == NAME).delete()
        db.commit()
    finally:
        db.close()


def _post(rule_type, params=None):
    return client.post("/rules", json={
        "dataset_name": NAME, "column_name": "c",
        "rule_type": rule_type, "rule_params": params or {},
    })


def test_rules_crud():
    try:
        resp = _post("not_null")
        assert resp.status_code == 200
        rid = resp.json()["id"]

        listed = client.get(f"/rules?dataset={NAME}").json()
        assert [r["id"] for r in listed] == [rid]

        assert client.delete(f"/rules/{rid}").status_code == 200
        assert client.get(f"/rules?dataset={NAME}").json() == []
    finally:
        _cleanup()


def test_rejects_unknown_rule_type():
    try:
        assert _post("banana").status_code == 400
        assert client.get(f"/rules?dataset={NAME}").json() == []
    finally:
        _cleanup()


def test_in_set_needs_allowed_list():
    try:
        assert _post("in_set").status_code == 400
        assert _post("in_set", {"allowed": ["a", "b"]}).status_code == 200
    finally:
        _cleanup()


def test_regex_rejects_bad_pattern():
    try:
        assert _post("regex", {"pattern": "("}).status_code == 400
        assert _post("regex", {}).status_code == 400
        assert _post("regex", {"pattern": "^C[0-9]+$"}).status_code == 200
    finally:
        _cleanup()
