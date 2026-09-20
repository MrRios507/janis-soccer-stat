from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    season_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("seasons.id"), nullable=False)
    home_team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    venue_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("venues.id"))
    referee_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("referees.id"))
    kickoff_utc: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    local_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    stage: Mapped[Optional[str]] = mapped_column(String(30))
    round: Mapped[Optional[str]] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    neutral_venue: Mapped[bool] = mapped_column(Boolean, nullable=False)
    home_score: Mapped[Optional[int]] = mapped_column(Integer)
    away_score: Mapped[Optional[int]] = mapped_column(Integer)
    home_score_ht: Mapped[Optional[int]] = mapped_column(Integer)
    away_score_ht: Mapped[Optional[int]] = mapped_column(Integer)
    home_score_et: Mapped[Optional[int]] = mapped_column(Integer)
    away_score_et: Mapped[Optional[int]] = mapped_column(Integer)
    home_pens: Mapped[Optional[int]] = mapped_column(Integer)
    away_pens: Mapped[Optional[int]] = mapped_column(Integer)
    attendance: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    last_scraped_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        # UC-001 BR-001: while every pair of teams meets once at each ground, the
        # season and the two teams identify the match, so reloading a season
        # updates it instead of adding it again.
        UniqueConstraint("season_id", "home_team_id", "away_team_id"),
        CheckConstraint("home_team_id <> away_team_id", name="home_away_different"),
        CheckConstraint(
            "status IN ('scheduled','live','finished','postponed','cancelled')",
            name="status_valid",
        ),
        CheckConstraint(
            "status <> 'finished' OR (home_score IS NOT NULL AND away_score IS NOT NULL)",
            name="finished_has_scores",
        ),
        CheckConstraint(
            "(home_score_et IS NULL OR home_score IS NOT NULL)"
            " AND (away_score_et IS NULL OR away_score IS NOT NULL)",
            name="extra_time_requires_regular_time",
        ),
        # FR-014 / NFR-001: a team's history is always read in chronological
        # order, and a team is home in half of it and away in the other half.
        Index("ix_matches_home_team_kickoff", "home_team_id", "kickoff_utc"),
        Index("ix_matches_away_team_kickoff", "away_team_id", "kickoff_utc"),
    )


class MatchTeamStats(Base):
    __tablename__ = "match_team_stats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("matches.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sources.id"), nullable=False)
    is_home: Mapped[bool] = mapped_column(Boolean, nullable=False)
    shots: Mapped[Optional[int]] = mapped_column(Integer)
    shots_on_target: Mapped[Optional[int]] = mapped_column(Integer)
    woodwork: Mapped[Optional[int]] = mapped_column(Integer)
    corners: Mapped[Optional[int]] = mapped_column(Integer)
    offsides: Mapped[Optional[int]] = mapped_column(Integer)
    fouls: Mapped[Optional[int]] = mapped_column(Integer)
    yellow_cards: Mapped[Optional[int]] = mapped_column(Integer)
    red_cards: Mapped[Optional[int]] = mapped_column(Integer)

    __table_args__ = (UniqueConstraint("match_id", "team_id", "source_id"),)
