from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MatchFeatures(Base):
    __tablename__ = "match_features"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("matches.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    as_of: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    feature_set_version: Mapped[str] = mapped_column(String(20), nullable=False)
    features: Mapped[str] = mapped_column(String(4000), nullable=False)
    is_complete: Mapped[bool] = mapped_column(Boolean, nullable=False)
    history_matches: Mapped[int] = mapped_column(Integer, nullable=False)
    computed_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("match_id", "team_id", "feature_set_version", "as_of"),
    )


class PredictiveModel(Base):
    """A trained model version (entity MODELS). Named PredictiveModel, not
    Model, to avoid confusion with "ORM model" in conversation and code."""

    __tablename__ = "models"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False)
    feature_set_version: Mapped[str] = mapped_column(String(20), nullable=False)
    train_start: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    train_end: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    metrics: Mapped[Optional[str]] = mapped_column(String(2000))
    artifact_path: Mapped[Optional[str]] = mapped_column(String(500))
    trained_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "version"),
        CheckConstraint("train_end > train_start", name="train_end_after_start"),
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("matches.id"), nullable=False)
    model_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("models.id"), nullable=False)
    as_of: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    p_home: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    p_draw: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    p_away: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    exp_goals_home: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    exp_goals_away: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    predicted_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("match_id", "model_id", "as_of"),
        CheckConstraint("p_home BETWEEN 0 AND 1", name="p_home_in_range"),
        CheckConstraint("p_draw BETWEEN 0 AND 1", name="p_draw_in_range"),
        CheckConstraint("p_away BETWEEN 0 AND 1", name="p_away_in_range"),
        CheckConstraint(
            "abs(p_home + p_draw + p_away - 1) < 0.000001", name="probabilities_sum_to_one"
        ),
    )
