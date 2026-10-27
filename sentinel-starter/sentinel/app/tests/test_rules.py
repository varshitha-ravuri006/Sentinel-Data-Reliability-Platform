from app.schemas.contracts import Rule
from app.services.engine import validate


def _run(rows, rules):
    return validate(rows, rules)


def test_not_null():
    rows = [{"customer_id": "C1"}, {"customer_id": ""}, {"customer_id": None}]
    r = _run(rows, [Rule(column="customer_id", rule_type="not_null")])
    assert r.valid_count == 1
    assert r.invalid_count == 2


def test_positive():
    rows = [{"amount": "5"}, {"amount": "-3"}, {"amount": "0"}, {"amount": "x"}]
    r = _run(rows, [Rule(column="amount", rule_type="positive")])
    assert r.valid_count == 1
    assert r.invalid_count == 3


def test_in_set():
    rows = [{"status": "paid"}, {"status": "unknown"}]
    rule = Rule(column="status", rule_type="in_set",
                params={"allowed": ["pending", "paid", "shipped", "cancelled"]})
    r = _run(rows, [rule])
    assert r.valid_count == 1
    assert r.invalid_count == 1
