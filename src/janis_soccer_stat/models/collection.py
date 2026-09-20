from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
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
    # Polymorphic reference, kept as a plain column: held_kind names only teams
    # in increment 1, and widens to matches and players with the increments that
    # collect them (UC-014 BR-004).
    resolved_ref: Mapped[Optional[int]] = mapped_column(BigInteger)
    held_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("held_kind IN ('team')", name="held_kind_valid"),
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
