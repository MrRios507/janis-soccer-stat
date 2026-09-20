"""UC-015 Configure Collection Scope.

Reads the declaration in collection_scope.toml and registers the competitions,
their seasons and the sources that feed them. Applying it again updates what is
already declared rather than registering it twice (A1), so the whole thing is
safe to rerun.
"""

from __future__ import annotations

import datetime
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .models import Competition, Country, Season, Source
from .seeding import UpsertCount

SCOPE_FILE = Path("collection_scope.toml")

CAUTIOUS_RATE_LIMIT_MS = 2000
"""The delay applied to a source that publishes none of its own (UC-015 A3)."""


class ScopeError(Exception):
    """The declaration cannot be applied, and nothing was written."""


@dataclass(frozen=True)
class SeasonRefusal:
    """A season left unregistered because its window collides with another."""

    competition: str
    label: str
    collides_with: str


@dataclass
class ScopeReport:
    competitions: UpsertCount
    seasons: UpsertCount
    sources: UpsertCount
    refused: list[SeasonRefusal] = field(default_factory=list)


def season_label(year_start: int) -> str:
    """The season beginning in 2005 is known as 2005-06."""
    return f"{year_start}-{(year_start + 1) % 100:02d}"


def season_window(year_start: int) -> tuple[datetime.date, datetime.date]:
    """The conventional window of play, which never overlaps the next season's.

    UC-001 may narrow it later to the first and last match actually played.
    """
    return datetime.date(year_start, 7, 1), datetime.date(year_start + 1, 6, 30)


def load_declaration(path: Path | None = None) -> dict[str, Any]:
    path = path or SCOPE_FILE
    if not path.exists():
        raise ScopeError(f"No scope declaration at {path}.")
    with path.open("rb") as handle:
        declaration = tomllib.load(handle)

    seasons = declaration.get("seasons", {})
    first, last, current = seasons.get("first"), seasons.get("last"), seasons.get("current")
    if first is None or last is None or current is None:
        raise ScopeError("The [seasons] table must declare first, last and current.")
    if first > last:
        raise ScopeError(f"The first season ({first}) is later than the last ({last}).")
    if not first <= current <= last:
        raise ScopeError(f"The current season ({current}) is outside {first}-{last}.")
    if not declaration.get("competitions"):
        raise ScopeError("The declaration lists no competition.")
    return declaration


def apply_scope(session: Session, declaration: dict[str, Any]) -> ScopeReport:
    seasons = declaration["seasons"]
    first, last, current = seasons["first"], seasons["last"], seasons["current"]
    current_label = season_label(current)

    countries = dict(session.execute(select(Country.fifa_code, Country.id)).all())
    declared = declaration["competitions"]
    missing = sorted({c["country"] for c in declared} - countries.keys())
    if missing:
        raise ScopeError(
            f"Unknown countries: {', '.join(missing)}. "
            "Register them first with `janis-soccer-stat seed-countries`."
        )

    competition_ids, competitions = _register_competitions(session, declared, countries)
    seasons_written, refused = _register_seasons(
        session, declared, competition_ids, first, last, current_label
    )
    sources = _register_sources(session, declaration.get("sources", []))
    return ScopeReport(competitions, seasons_written, sources, refused)


def _register_competitions(
    session: Session, declared: list[dict[str, Any]], countries: dict[str, int]
) -> tuple[dict[str, int], UpsertCount]:
    rows = [
        {
            "name": c["name"],
            "country_id": countries[c["country"]],
            "format": c["format"],
            "scope": c["scope"],
            "tier": c.get("tier"),
            "gender": c["gender"],
            "is_collected": c.get("is_collected", True),
        }
        for c in declared
    ]
    known = set(session.execute(select(Competition.name, Competition.country_id)).all())
    statement = insert(Competition).values(rows)
    result = session.execute(
        statement.on_conflict_do_update(
            index_elements=["name", "country_id"],
            set_={
                "format": statement.excluded.format,
                "scope": statement.excluded.scope,
                "tier": statement.excluded.tier,
                "gender": statement.excluded.gender,
                "is_collected": statement.excluded.is_collected,
            },
        ).returning(Competition.id, Competition.name)
    )
    inserted = sum(1 for row in rows if (row["name"], row["country_id"]) not in known)
    return {name: id_ for id_, name in result}, UpsertCount(inserted, len(rows) - inserted)


def _register_seasons(
    session: Session,
    declared: list[dict[str, Any]],
    competition_ids: dict[str, int],
    first: int,
    last: int,
    current_label: str,
) -> tuple[UpsertCount, list[SeasonRefusal]]:
    ids = [competition_ids[c["name"]] for c in declared]
    existing = session.execute(
        select(Season.competition_id, Season.label, Season.start_date, Season.end_date).where(
            Season.competition_id.in_(ids)
        )
    ).all()
    known = {(competition_id, label) for competition_id, label, _, _ in existing}

    rows: list[dict[str, Any]] = []
    refused: list[SeasonRefusal] = []
    for competition in declared:
        competition_id = competition_ids[competition["name"]]
        windows = [
            (label, start, end)
            for cid, label, start, end in existing
            if cid == competition_id and start and end
        ]
        for year in range(first, last + 1):
            label = season_label(year)
            start, end = season_window(year)
            # A2: a declared window may not overlap another season of the same
            # competition, so that every match falls in exactly one (BR-004).
            collision = next(
                (other for other, other_start, other_end in windows
                 if other != label and other_start <= end and start <= other_end),
                None,
            )
            if collision:
                refused.append(SeasonRefusal(competition["name"], label, collision))
                continue
            rows.append({
                "competition_id": competition_id,
                "label": label,
                "year_start": year,
                "start_date": start,
                "end_date": end,
                "is_current": label == current_label,
            })

    if not rows:
        return UpsertCount(0, 0), refused

    statement = insert(Season).values(rows)
    session.execute(
        statement.on_conflict_do_update(
            index_elements=["competition_id", "label"],
            set_={
                "year_start": statement.excluded.year_start,
                "start_date": statement.excluded.start_date,
                "end_date": statement.excluded.end_date,
                "is_current": statement.excluded.is_current,
            },
        )
    )
    # Exactly one season per competition is the one being played, including when
    # the declaration moves it or when an older season was marked by hand.
    session.execute(
        update(Season)
        .where(Season.competition_id.in_(ids), Season.label != current_label)
        .values(is_current=False)
    )
    inserted = sum(1 for row in rows if (row["competition_id"], row["label"]) not in known)
    return UpsertCount(inserted, len(rows) - inserted), refused


def _register_sources(session: Session, declared: list[dict[str, Any]]) -> UpsertCount:
    if not declared:
        return UpsertCount(0, 0)
    rows = []
    for source in declared:
        # BR-003: a source that states no limit is given the most cautious delay
        # this system knows, never none, and the assumption is recorded.
        rate_limit_ms = source.get("rate_limit_ms")
        assumed = source.get("rate_limit_is_assumed", rate_limit_ms is None)
        if not rate_limit_ms:
            rate_limit_ms, assumed = CAUTIOUS_RATE_LIMIT_MS, True
        rows.append({
            "slug": source["slug"],
            "name": source["name"],
            "base_url": source["base_url"],
            "rate_limit_ms": rate_limit_ms,
            "rate_limit_is_assumed": assumed,
            "is_active": source.get("is_active", True),
        })

    known = set(session.scalars(select(Source.slug)))
    statement = insert(Source).values(rows)
    session.execute(
        statement.on_conflict_do_update(
            index_elements=["slug"],
            set_={
                "name": statement.excluded.name,
                "base_url": statement.excluded.base_url,
                "rate_limit_ms": statement.excluded.rate_limit_ms,
                "rate_limit_is_assumed": statement.excluded.rate_limit_is_assumed,
                "is_active": statement.excluded.is_active,
            },
        )
    )
    inserted = sum(1 for row in rows if row["slug"] not in known)
    return UpsertCount(inserted, len(rows) - inserted)


def describe_scope(session: Session) -> str:
    """What the database currently considers in scope."""
    lines: list[str] = []
    rows = session.execute(
        select(Competition, Country.fifa_code)
        .outerjoin(Country, Competition.country_id == Country.id)
        .order_by(Competition.name)
    ).all()
    if not rows:
        return "No competition is declared. Apply a scope with `scope-apply`."

    lines.append("Competitions")
    for competition, code in rows:
        seasons = session.execute(
            select(Season.label, Season.is_current)
            .where(Season.competition_id == competition.id)
            .order_by(Season.year_start)
        ).all()
        current = next((label for label, is_current in seasons if is_current), "none")
        span = f"{seasons[0][0]} to {seasons[-1][0]}" if seasons else "no seasons"
        collected = "collected" if competition.is_collected else "withdrawn"
        lines.append(
            f"  {competition.name} ({code}, tier {competition.tier}, {collected}): "
            f"{len(seasons)} seasons, {span}, currently {current}"
        )

    lines.append("Sources")
    for source in session.scalars(select(Source).order_by(Source.slug)):
        assumed = " (assumed)" if source.rate_limit_is_assumed else " (stated)"
        active = "active" if source.is_active else "inactive"
        lines.append(
            f"  {source.slug}: {source.base_url}, "
            f"{source.rate_limit_ms} ms between requests{assumed}, {active}"
        )
    return "\n".join(lines)
