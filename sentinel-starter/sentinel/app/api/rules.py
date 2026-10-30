import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.tables import ValidationRule

router = APIRouter(prefix="/rules", tags=["contracts"])

VALID_RULE_TYPES = {"not_null", "positive", "in_set", "valid_date", "unique", "regex"}


class RuleIn(BaseModel):
    dataset_name: str
    column_name: str
    rule_type: str
    rule_params: dict = {}


def _check_rule(rule: RuleIn) -> None:
    """Reject rules the engine could not run, instead of failing later."""
    if rule.rule_type not in VALID_RULE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"rule_type must be one of {sorted(VALID_RULE_TYPES)}",
        )
    params = rule.rule_params
    if rule.rule_type == "in_set":
        allowed = params.get("allowed")
        if not isinstance(allowed, list) or not allowed:
            raise HTTPException(
                status_code=400,
                detail='in_set needs params like {"allowed": ["a", "b"]}',
            )
    if rule.rule_type == "regex":
        pattern = params.get("pattern")
        if not isinstance(pattern, str) or not pattern:
            raise HTTPException(
                status_code=400,
                detail='regex needs params like {"pattern": "^C[0-9]+$"}',
            )
        try:
            re.compile(pattern)
        except re.error:
            raise HTTPException(status_code=400, detail="regex pattern is not valid")


@router.post("")
def create_rule(rule: RuleIn, db: Session = Depends(get_db)):
    _check_rule(rule)
    r = ValidationRule(**rule.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"id": r.id}


@router.get("")
def list_rules(dataset: str, db: Session = Depends(get_db)):
    rows = db.query(ValidationRule).filter(
        ValidationRule.dataset_name == dataset).all()
    return [
        {"id": r.id, "column": r.column_name,
         "rule_type": r.rule_type, "params": r.rule_params}
        for r in rows
    ]


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    db.query(ValidationRule).filter(ValidationRule.id == rule_id).delete()
    db.commit()
    return {"deleted": rule_id}
