from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.tables import ValidationRule

router = APIRouter(prefix="/rules", tags=["contracts"])


class RuleIn(BaseModel):
    dataset_name: str
    column_name: str
    rule_type: str
    rule_params: dict = {}


@router.post("")
def create_rule(rule: RuleIn, db: Session = Depends(get_db)):
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
