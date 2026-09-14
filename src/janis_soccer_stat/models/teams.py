from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column(String(50))
    country_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("countries.id"))
    founded_year: Mapped[Optional[int]] = mapped_column(Integer)
    is_national_team: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class TeamAlias(Base):
    __tablename__ = "team_aliases"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    alias: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (UniqueConstraint("team_id", "normalized"),)
