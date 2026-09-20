"""Reference data that ships with the code.

Countries are owned by no use case: they are the precondition UC-015 assumes,
and they change about as often as the political map. Seeding them is an upsert,
so running it again is always safe.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .models import Country

COUNTRIES_FILE = Path(__file__).parent / "data" / "countries.toml"


@dataclass(frozen=True)
class UpsertCount:
    """How a write divided between rows that were new and rows already there."""

    inserted: int
    updated: int

    @property
    def total(self) -> int:
        return self.inserted + self.updated

    def __str__(self) -> str:
        return f"{self.inserted} inserted, {self.updated} updated"


def load_countries(path: Path | None = None) -> list[dict[str, str]]:
    with (path or COUNTRIES_FILE).open("rb") as handle:
        return tomllib.load(handle)["countries"]


def seed_countries(session: Session, countries: list[dict[str, str]] | None = None) -> UpsertCount:
    rows = load_countries() if countries is None else countries
    if not rows:
        return UpsertCount(0, 0)

    known = set(session.scalars(select(Country.name)))
    statement = insert(Country).values(rows)
    session.execute(
        statement.on_conflict_do_update(
            index_elements=["name"],
            set_={
                "fifa_code": statement.excluded.fifa_code,
                "confederation": statement.excluded.confederation,
            },
        )
    )
    inserted = sum(1 for row in rows if row["name"] not in known)
    return UpsertCount(inserted, len(rows) - inserted)
