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
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
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
    )


class MatchWeather(Base):
    __tablename__ = "match_weather"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("matches.id"), nullable=False, unique=True
    )
    temperature_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    humidity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    wind_kmh: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    precipitation_mm: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    condition: Mapped[Optional[str]] = mapped_column(String(50))


class MatchTeamStats(Base):
    __tablename__ = "match_team_stats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("matches.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sources.id"), nullable=False)
    is_home: Mapped[bool] = mapped_column(Boolean, nullable=False)
    xg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    xg_non_penalty: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    shots: Mapped[Optional[int]] = mapped_column(Integer)
    shots_on_target: Mapped[Optional[int]] = mapped_column(Integer)
    shots_off_target: Mapped[Optional[int]] = mapped_column(Integer)
    shots_blocked: Mapped[Optional[int]] = mapped_column(Integer)
    shots_inside_box: Mapped[Optional[int]] = mapped_column(Integer)
    big_chances: Mapped[Optional[int]] = mapped_column(Integer)
    big_chances_missed: Mapped[Optional[int]] = mapped_column(Integer)
    woodwork: Mapped[Optional[int]] = mapped_column(Integer)
    possession: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    passes: Mapped[Optional[int]] = mapped_column(Integer)
    passes_completed: Mapped[Optional[int]] = mapped_column(Integer)
    crosses: Mapped[Optional[int]] = mapped_column(Integer)
    corners: Mapped[Optional[int]] = mapped_column(Integer)
    offsides: Mapped[Optional[int]] = mapped_column(Integer)
    fouls: Mapped[Optional[int]] = mapped_column(Integer)
    yellow_cards: Mapped[Optional[int]] = mapped_column(Integer)
    red_cards: Mapped[Optional[int]] = mapped_column(Integer)
    tackles: Mapped[Optional[int]] = mapped_column(Integer)
    interceptions: Mapped[Optional[int]] = mapped_column(Integer)
    clearances: Mapped[Optional[int]] = mapped_column(Integer)
    saves: Mapped[Optional[int]] = mapped_column(Integer)
    duels_won: Mapped[Optional[int]] = mapped_column(Integer)
    aerials_won: Mapped[Optional[int]] = mapped_column(Integer)

    __table_args__ = (
        UniqueConstraint("match_id", "team_id", "source_id"),
        CheckConstraint(
            "passes_completed IS NULL OR passes IS NULL OR passes_completed <= passes",
            name="completed_passes_within_attempted",
        ),
    )


class MatchEvent(Base):
    __tablename__ = "match_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("matches.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    player_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("players.id"))
    related_player_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("players.id"))
    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    added_time: Mapped[Optional[int]] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    detail: Mapped[Optional[str]] = mapped_column(String(100))

    __table_args__ = (
        CheckConstraint("minute BETWEEN 0 AND 120", name="minute_in_range"),
        CheckConstraint(
            "event_type IN ('goal','own_goal','penalty_scored','penalty_missed',"
            "'yellow_card','red_card','substitution','var_review')",
            name="event_type_valid",
        ),
        CheckConstraint(
            "event_type <> 'substitution'"
            " OR (player_id IS NOT NULL AND related_player_id IS NOT NULL)",
            name="substitution_has_both_players",
        ),
    )


class MatchOdds(Base):
    __tablename__ = "match_odds"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("matches.id"), nullable=False)
    bookmaker_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bookmakers.id"), nullable=False
    )
    market: Mapped[str] = mapped_column(String(30), nullable=False)
    selection: Mapped[str] = mapped_column(String(20), nullable=False)
    line: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_closing: Mapped[bool] = mapped_column(Boolean, nullable=False)
    recorded_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "match_id", "bookmaker_id", "market", "selection", "line", "recorded_at"
        ),
        CheckConstraint(
            "market IN ('1x2','over_under','asian_handicap','btts')", name="market_valid"
        ),
        CheckConstraint(
            "selection IN ('home','draw','away','over','under','yes','no')",
            name="selection_valid",
        ),
        CheckConstraint(
            "market NOT IN ('over_under','asian_handicap') OR line IS NOT NULL",
            name="line_required_for_totals_and_handicaps",
        ),
        CheckConstraint("market <> '1x2' OR line IS NULL", name="line_absent_for_1x2"),
        Index(
            "ix_match_odds_one_closing_per_selection",
            "match_id",
            "bookmaker_id",
            "market",
            "selection",
            unique=True,
            postgresql_where=text("is_closing"),
        ),
    )
