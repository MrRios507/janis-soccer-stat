from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sources.id"), nullable=False)
    target: Mapped[str] = mapped_column(String(200), nullable=False)
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    items_found: Mapped[Optional[int]] = mapped_column(Integer)
    items_upserted: Mapped[Optional[int]] = mapped_column(Integer)
    items_failed: Mapped[Optional[int]] = mapped_column(Integer)
    resume_point: Mapped[Optional[str]] = mapped_column(String(200))
    error: Mapped[Optional[str]] = mapped_column(String(2000))

    __table_args__ = (
        CheckConstraint(
            "status IN ('running','ok','failed','partial','abandoned')", name="status_valid"
        ),
        CheckConstraint(
            "finished_at IS NULL OR finished_at > started_at", name="finish_after_start"
        ),
        CheckConstraint("status <> 'running' OR finished_at IS NULL", name="running_has_no_finish"),
        CheckConstraint(
            "status <> 'partial' OR resume_point IS NOT NULL", name="partial_has_resume_point"
        ),
        Index(
            "ix_scrape_runs_one_running_per_source_target",
            "source_id",
            "target",
            unique=True,
            postgresql_where=text("status = 'running'"),
        ),
    )


class RawDocument(Base):
    __tablename__ = "raw_documents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    scrape_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("scrape_runs.id"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    # Unbounded raw payload (spec caps it at 1,000,000 chars) — Text fits a
    # blob of unknown/variable size better than a VARCHAR(n) that large.
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    fetched_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    parsed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    reading_version: Mapped[Optional[str]] = mapped_column(String(20))
    parse_error: Mapped[Optional[str]] = mapped_column(String(2000))

    __table_args__ = (
        CheckConstraint(
            "parsed_at IS NULL OR reading_version IS NOT NULL",
            name="parsed_requires_reading_version",
        ),
    )


class TeamSource(Base):
    __tablename__ = "team_sources"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=False)
    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sources.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    external_name: Mapped[Optional[str]] = mapped_column(String(200))

    __table_args__ = (UniqueConstraint("source_id", "external_id"),)


class MatchSource(Base):
    __tablename__ = "match_sources"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    match_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("matches.id"), nullable=False)
    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sources.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(500))

    __table_args__ = (UniqueConstraint("source_id", "external_id"),)


class CompetitionSource(Base):
    __tablename__ = "competition_sources"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    competition_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("competitions.id"), nullable=False
    )
    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sources.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (UniqueConstraint("source_id", "external_id"),)


class HeldRecord(Base):
    __tablename__ = "held_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    scrape_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("scrape_runs.id"), nullable=False
    )
    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sources.id"), nullable=False)
    held_kind: Mapped[str] = mapped_column(String(20), nullable=False)
    published_value: Mapped[str] = mapped_column(String(200), nullable=False)
    context: Mapped[Optional[str]] = mapped_column(String(500))
    candidates: Mapped[Optional[str]] = mapped_column(String(2000))
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    # Polymorphic reference to TEAMS, MATCHES or PLAYERS depending on held_kind:
    # no single target table, so this cannot be a real ForeignKey.
    resolved_ref: Mapped[Optional[int]] = mapped_column(BigInteger)
    held_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("held_kind IN ('team','match','player')", name="held_kind_valid"),
        CheckConstraint(
            "status IN ('pending','resolved','discarded')", name="status_valid"
        ),
        CheckConstraint(
            "(status <> 'resolved' OR (resolved_ref IS NOT NULL AND resolved_at IS NOT NULL))"
            " AND (status <> 'pending' OR (resolved_ref IS NULL AND resolved_at IS NULL))",
            name="resolution_fields_match_status",
        ),
        Index(
            "ix_held_records_unique_while_pending",
            "source_id",
            "held_kind",
            "published_value",
            unique=True,
            postgresql_where=text("status = 'pending'"),
        ),
    )


class SourceCoverage(Base):
    __tablename__ = "source_coverage"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("sources.id"), nullable=False)
    competition_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("competitions.id"), nullable=False
    )
    statistic: Mapped[str] = mapped_column(String(50), nullable=False)
    is_offered: Mapped[bool] = mapped_column(Boolean, nullable=False)
    first_season: Mapped[Optional[str]] = mapped_column(String(20))

    __table_args__ = (
        UniqueConstraint("source_id", "competition_id", "statistic"),
        CheckConstraint(
            "is_offered OR first_season IS NULL", name="no_first_season_when_not_offered"
        ),
    )
