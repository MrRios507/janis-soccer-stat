from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    scope: Mapped[str] = mapped_column(String(20), nullable=False)
    country_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("countries.id"))
    confederation: Mapped[Optional[str]] = mapped_column(String(20))
    tier: Mapped[Optional[int]] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    is_collected: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __table_args__ = (
        # UC-015 A1 recognises a competition already declared, and BR-001 relies
        # on it: without a natural key a typo would silently create a second one.
        UniqueConstraint("name", "country_id"),
        CheckConstraint("format IN ('league','cup','group_knockout')", name="format_valid"),
        CheckConstraint(
            "scope IN ('domestic','continental','international')", name="scope_valid"
        ),
        CheckConstraint("gender IN ('male','female')", name="gender_valid"),
    )


class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    competition_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("competitions.id"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(20), nullable=False)
    year_start: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    num_teams: Mapped[Optional[int]] = mapped_column(Integer)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __table_args__ = (
        UniqueConstraint("competition_id", "label"),
        CheckConstraint(
            "end_date IS NULL OR start_date IS NULL OR end_date > start_date",
            name="end_after_start",
        ),
    )
