"""First test: prove the engine splits good rows from bad ones.

5 rows, 2 have a missing customer_id -> expect 3 valid, 2 invalid, health 60%.
Run it with:  docker compose exec app pytest -q
It FAILS until you implement _not_null in services/engine.py. That's the point.
"""
from app.schemas.contracts import Rule
from app.services.engine import validate


def test_not_null_splits_valid_and_invalid():
    rows = [
        {"order_id": "1", "customer_id": "C1"},
        {"order_id": "2", "customer_id": ""},     # missing
        {"order_id": "3", "customer_id": "C3"},
        {"order_id": "4", "customer_id": None},    # missing
        {"order_id": "5", "customer_id": "C5"},
    ]
    rules = [Rule(column="customer_id", rule_type="not_null")]

    result = validate(rows, rules)

    assert result.total_rows == 5
    assert result.valid_count == 3
    assert result.invalid_count == 2
    assert result.health_score == 60.0
def test_positive_splits_valid_and_invalid():
    rows = [
        {"order_id": "1", "amount": "50"},
        {"order_id": "2", "amount": "-5"},    # not positive
        {"order_id": "3", "amount": "10"},
        {"order_id": "4", "amount": "0"},     # not positive (zero fails)
        {"order_id": "5", "amount": "abc"},   # not numeric
    ]
    rules = [Rule(column="amount", rule_type="positive")]
    result = validate(rows, rules)
    assert result.total_rows == 5
    assert result.valid_count == 2
    assert result.invalid_count == 3
    assert result.health_score == 40.0


def test_in_set_splits_valid_and_invalid():
    rows = [
        {"order_id": "1", "status": "paid"},
        {"order_id": "2", "status": "unknown"},   # not allowed
        {"order_id": "3", "status": "pending"},
        {"order_id": "4", "status": "shipped"},
        {"order_id": "5", "status": "refunded"},  # not allowed
    ]
    rules = [
        Rule(
            column="status",
            rule_type="in_set",
            params={"allowed": ["pending", "paid", "shipped", "cancelled"]},
        )
    ]
    result = validate(rows, rules)
    assert result.total_rows == 5
    assert result.valid_count == 3
    assert result.invalid_count == 2
    assert round(result.health_score, 2) == 60.0