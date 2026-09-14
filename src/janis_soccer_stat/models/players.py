from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    country_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("countries.id"))
    position: Mapped[Optional[str]] = mapped_column(String(30))
    preferred_foot: Mapped[Optional[str]] = mapped_column(String(10))


class PlayerTeamSpell(Base):
    __tablename__ = "player_team_spells"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    player_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("players.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)

    __table_args__ = (
        CheckConstraint("end_date IS NULL OR end_date > start_date", name="end_after_start"),
    )


class Lineup(Base):
    __tablename__ = "lineups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("matches.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    player_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("players.id"), nullable=False)
    is_starter: Mapped[bool] = mapped_column(Boolean, nullable=False)
    position: Mapped[Optional[str]] = mapped_column(String(30))
    shirt_number: Mapped[Optional[int]] = mapped_column(Integer)
    minutes_played: Mapped[Optional[int]] = mapped_column(Integer)

    __table_args__ = (UniqueConstraint("match_id", "player_id"),)


class PlayerMatchStats(Base):
    __tablename__ = "player_match_stats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("matches.id"), nullable=False)
    player_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("players.id"), nullable=False)
    minutes: Mapped[Optional[int]] = mapped_column(Integer)
    goals: Mapped[Optional[int]] = mapped_column(Integer)
    assists: Mapped[Optional[int]] = mapped_column(Integer)
    xg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    xa: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    shots: Mapped[Optional[int]] = mapped_column(Integer)
    key_passes: Mapped[Optional[int]] = mapped_column(Integer)

    __table_args__ = (UniqueConstraint("match_id", "player_id"),)


class PlayerAvailability(Base):
    __tablename__ = "player_availability"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    player_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("players.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    reason: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    origin: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint("end_date IS NULL OR end_date > start_date", name="end_after_start"),
        CheckConstraint(
            "reason IN ('injury','suspension','international_duty','personal','other')",
            name="reason_valid",
        ),
        CheckConstraint("status IN ('out','doubtful')", name="status_valid"),
        CheckConstraint("origin IN ('reported','derived')", name="origin_valid"),
        CheckConstraint(
            "origin <> 'derived' OR reason = 'other'", name="derived_reason_is_other"
        ),
    )


class Shot(Base):
    __tablename__ = "shots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("matches.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    player_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("players.id"))
    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    x: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    y: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    xg: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    body_part: Mapped[Optional[str]] = mapped_column(String(20))
    situation: Mapped[str] = mapped_column(String(30), nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint("minute BETWEEN 0 AND 120", name="minute_in_range"),
        CheckConstraint("x BETWEEN 0 AND 1", name="x_in_range"),
        CheckConstraint("y BETWEEN 0 AND 1", name="y_in_range"),
        CheckConstraint("xg BETWEEN 0 AND 1", name="xg_in_range"),
        CheckConstraint(
            "situation IN ('open_play','corner','free_kick','penalty','set_piece')",
            name="situation_valid",
        ),
        CheckConstraint(
            "result IN ('goal','saved','blocked','off_target','woodwork')", name="result_valid"
        ),
    )
