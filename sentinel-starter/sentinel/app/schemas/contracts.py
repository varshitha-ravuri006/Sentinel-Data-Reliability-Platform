"""The contract between ingestion and the engine.

A Rule goes IN (one check to run on one column).
A ValidationResult comes OUT (what passed, what failed, and why).
Both teammates build against these shapes.
"""
from typing import Any

from pydantic import BaseModel, Field


class Rule(BaseModel):
    column: str
    # not_null | positive | in_set | valid_date | unique | regex
    rule_type: str
    params: dict[str, Any] = Field(default_factory=dict)


class RowFailure(BaseModel):
    column: str
    rule_type: str
    detail: str


class InvalidRow(BaseModel):
    row_number: int
    data: dict
    reasons: list[RowFailure]


class ValidationResult(BaseModel):
    total_rows: int
    valid_count: int
    invalid_count: int
    health_score: float
    valid_rows: list[dict]
    invalid_rows: list[InvalidRow]