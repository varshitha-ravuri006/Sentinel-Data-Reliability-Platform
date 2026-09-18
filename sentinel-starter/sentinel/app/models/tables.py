from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Dataset(Base):
    """One uploaded file + its validation summary."""
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    source_filename: Mapped[str] = mapped_column(String(512))
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0)
    health_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="uploaded")

    valid_records: Mapped[list["ValidRecord"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )
    quarantined: Mapped[list["Quarantine"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )


class ValidationRule(Base):
    """A single clause of a data contract. Rules are DATA, not code."""
    __tablename__ = "validation_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_name: Mapped[str] = mapped_column(String(255), index=True)
    column_name: Mapped[str] = mapped_column(String(255))
    # not_null | positive | in_set | valid_date | unique | regex
    rule_type: Mapped[str] = mapped_column(String(50))
    rule_params: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ValidRecord(Base):
    """A row that passed every rule. Full row stored as JSONB (any schema)."""
    __tablename__ = "valid_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    row_number: Mapped[int] = mapped_column(Integer)
    data: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    dataset: Mapped["Dataset"] = relationship(back_populates="valid_records")


class Quarantine(Base):
    """A row that failed >=1 rule, preserved intact with its failure reasons."""
    __tablename__ = "quarantine"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    row_number: Mapped[int] = mapped_column(Integer)
    data: Mapped[dict] = mapped_column(JSONB)
    # e.g. [{"column": "amount", "rule": "positive", "got": -5}]
    failure_reasons: Mapped[list] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    dataset: Mapped["Dataset"] = relationship(back_populates="quarantined")
class RawRecord(Base):
    """A row exactly as uploaded, before validation.The landing zone."""
    ___tablename___="raw_records"
    id:Mapped[int]=mapped_column(primary_key=True)
    dataset_id:Mapped[int]=mapped_column(ForeignKey("datasets.id"))
    row_number:Mapped[int]=mapped_column(Integer)
    data:Mapped[dict]= mapped_column(JSONB)
    