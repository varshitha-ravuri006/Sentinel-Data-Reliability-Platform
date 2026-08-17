"""The validation engine spine.

- RULES: a registry mapping a rule_type to the function that runs it.
- validate(): runs every rule on every row, sorts good vs bad, tallies results.

A rule function has the signature:  (value, params) -> error string OR None
Return None if the value passes. Return a short error string if it fails.
"""
from app.schemas.contracts import (
    InvalidRow,
    Rule,
    RowFailure,
    ValidationResult,
)


def _not_null(value, params):
    if value is None or value == "":
        return "value is required"
    return None


# The registry. More rule types get added here as you build them.
RULES = {
    "not_null": _not_null,
}


def validate(rows: list[dict], rules: list[Rule]) -> ValidationResult:
    valid_rows: list[dict] = []
    invalid_rows: list[InvalidRow] = []

    for i, row in enumerate(rows):
        reasons: list[RowFailure] = []
        for rule in rules:
            check = RULES.get(rule.rule_type)
            if check is None:
                continue  # unknown rule type — skip for now
            value = row.get(rule.column)
            error = check(value, rule.params)
            if error is not None:
                reasons.append(
                    RowFailure(
                        column=rule.column,
                        rule_type=rule.rule_type,
                        detail=error,
                    )
                )
        if reasons:
            invalid_rows.append(InvalidRow(row_number=i, data=row, reasons=reasons))
        else:
            valid_rows.append(row)

    total = len(rows)
    valid_count = len(valid_rows)
    invalid_count = len(invalid_rows)
    health = round(100 * valid_count / total, 2) if total else 0.0

    return ValidationResult(
        total_rows=total,
        valid_count=valid_count,
        invalid_count=invalid_count,
        health_score=health,
        valid_rows=valid_rows,
        invalid_rows=invalid_rows,
    )