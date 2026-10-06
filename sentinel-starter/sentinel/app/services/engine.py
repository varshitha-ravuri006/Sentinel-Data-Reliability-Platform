"""The validation engine.

Row-local rules are functions (value, params) -> error string | None,
registered in RULES. The 'unique' rule is column-global and handled specially
inside validate().
"""
import re
from datetime import datetime

from app.schemas.contracts import (
    InvalidRow, Rule, RowFailure, ValidationResult,
)


# ---- row-local rule functions ----

def _not_null(value, params):
    if value is None or value == "":
        return "value is required"
    return None


def _positive(value, params):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "must be a number"
    if n <= 0:
        return "must be greater than 0"
    return None


def _in_set(value, params):
    allowed = params.get("allowed", [])
    if value not in allowed:
        return f"must be one of {allowed}"
    return None


def _valid_date(value, params):
    fmt = params.get("format", "%Y-%m-%d")
    if value is None or value == "":
        return "date is required"
    try:
        datetime.strptime(value, fmt)
    except (TypeError, ValueError):
        return f"must be a valid date ({fmt})"
    return None


def _regex(value, params):
    pattern = params.get("pattern", "")
    if value is None or not re.match(pattern, str(value)):
        return "does not match required pattern"
    return None


# The registry of row-local rules. ('unique' is handled in validate().)
RULES = {
    "not_null": _not_null,
    "positive": _positive,
    "in_set": _in_set,
    "valid_date": _valid_date,
    "regex": _regex,
}


def validate(rows: list[dict], rules: list[Rule]) -> ValidationResult:
    # Pre-compute duplicate values for any 'unique' rules (column-global).
    unique_dupes: dict[str, set] = {}
    for rule in rules:
        if rule.rule_type == "unique":
            seen: dict = {}
            for row in rows:
                v = row.get(rule.column)
                seen[v] = seen.get(v, 0) + 1
            unique_dupes[rule.column] = {v for v, c in seen.items() if c > 1}

    valid_rows: list[dict] = []
    invalid_rows: list[InvalidRow] = []

    for i, row in enumerate(rows):
        reasons: list[RowFailure] = []
        for rule in rules:
            value = row.get(rule.column)
            if rule.rule_type == "unique":
                if value in unique_dupes.get(rule.column, set()):
                    reasons.append(RowFailure(
                        column=rule.column, rule_type="unique",
                        detail="duplicate value",
                    ))
                continue
            check = RULES.get(rule.rule_type)
            if check is None:
                continue
            error = check(value, rule.params)
            if error is not None:
                reasons.append(RowFailure(
                    column=rule.column, rule_type=rule.rule_type, detail=error,
                ))
        if reasons:
            invalid_rows.append(InvalidRow(row_number=i, data=row, reasons=reasons))
        else:
            valid_rows.append(row)

    total = len(rows)
    valid_count = len(valid_rows)
    invalid_count = len(invalid_rows)
    health = round(100 * valid_count / total, 2) if total else 0.0

    return ValidationResult(
        total_rows=total, valid_count=valid_count, invalid_count=invalid_count,
        health_score=health, valid_rows=valid_rows, invalid_rows=invalid_rows,
    )