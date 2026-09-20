from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from janis_soccer_stat.models import Competition, Season, Source
from janis_soccer_stat.scope import (
    CAUTIOUS_RATE_LIMIT_MS,
    ScopeError,
    apply_scope,
    load_declaration,
    season_label,
    season_window,
)
from janis_soccer_stat.seeding import seed_countries

TESTLAND = [{"name": "Testland", "fifa_code": "TST", "confederation": "UEFA"}]


def declaration(current: int = 2001) -> dict[str, Any]:
    return {
        "seasons": {"first": 2000, "last": 2002, "current": current},
        "competitions": [
            {
                "name": "Test League",
                "country": "TST",
                "format": "league",
                "scope": "domestic",
                "tier": 1,
                "gender": "male",
                "is_collected": True,
            }
        ],
        "sources": [
            {
                "slug": "test-source",
                "name": "Test Source",
                "base_url": "https://example.invalid/",
            }
        ],
    }


def seasons_of(session: Session, competition_id: int) -> list[Season]:
    return list(
        session.scalars(
            select(Season).where(Season.competition_id == competition_id).order_by(Season.year_start)
        )
    )


def only_competition(session: Session) -> Competition:
    competition = session.scalar(select(Competition).where(Competition.name == "Test League"))
    assert competition is not None
    return competition


# --- Labels and windows ------------------------------------------------------


@pytest.mark.parametrize(
    ("year", "label"),
    [(2005, "2005-06"), (2009, "2009-10"), (1999, "1999-00"), (2026, "2026-27")],
)
def test_season_label_follows_the_published_convention(year: int, label: str) -> None:
    assert season_label(year) == label


def test_consecutive_windows_do_not_overlap() -> None:
    _, first_end = season_window(2005)
    second_start, _ = season_window(2006)

    assert first_end < second_start
    assert season_window(2005)[0] == datetime.date(2005, 7, 1)


# --- The declaration ---------------------------------------------------------


def write(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    return path


def test_a_declaration_out_of_order_is_refused(tmp_path: Path) -> None:
    path = write(
        tmp_path / "scope.toml",
        '[seasons]\nfirst = 2010\nlast = 2005\ncurrent = 2006\n'
        '[[competitions]]\nname = "X"\ncountry = "TST"\nformat = "league"\n'
        'scope = "domestic"\ngender = "male"\n',
    )
    with pytest.raises(ScopeError, match="later than the last"):
        load_declaration(path)


def test_a_current_season_outside_the_range_is_refused(tmp_path: Path) -> None:
    path = write(
        tmp_path / "scope.toml",
        '[seasons]\nfirst = 2005\nlast = 2010\ncurrent = 2020\n'
        '[[competitions]]\nname = "X"\ncountry = "TST"\nformat = "league"\n'
        'scope = "domestic"\ngender = "male"\n',
    )
    with pytest.raises(ScopeError, match="outside 2005-2010"):
        load_declaration(path)


def test_a_missing_declaration_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ScopeError, match="No scope declaration"):
        load_declaration(tmp_path / "absent.toml")


def test_the_shipped_declaration_is_valid() -> None:
    shipped = load_declaration()

    assert len(shipped["competitions"]) == 5
    assert shipped["seasons"]["first"] == 2005


# --- Applying the scope ------------------------------------------------------


def test_an_undeclared_country_stops_the_whole_apply(session: Session) -> None:
    with pytest.raises(ScopeError, match="Unknown countries: TST"):
        apply_scope(session, declaration())

    assert session.scalar(
        select(func.count()).select_from(Competition).where(Competition.name == "Test League")
    ) == 0


def test_applying_twice_registers_once(session: Session) -> None:
    seed_countries(session, TESTLAND)

    first = apply_scope(session, declaration())
    second = apply_scope(session, declaration())

    assert (first.competitions.inserted, first.seasons.inserted, first.sources.inserted) == (1, 3, 1)
    assert (second.competitions.inserted, second.seasons.inserted, second.sources.inserted) == (
        0,
        0,
        0,
    )
    assert second.competitions.updated == 1
    assert second.seasons.updated == 3
    assert len(seasons_of(session, only_competition(session).id)) == 3


def test_exactly_one_season_is_current(session: Session) -> None:
    seed_countries(session, TESTLAND)
    apply_scope(session, declaration(current=2001))

    seasons = seasons_of(session, only_competition(session).id)
    current = [s.label for s in seasons if s.is_current]

    assert current == ["2001-02"]


def test_moving_the_current_season_does_not_add_rows(session: Session) -> None:
    seed_countries(session, TESTLAND)
    apply_scope(session, declaration(current=2001))

    apply_scope(session, declaration(current=2002))

    seasons = seasons_of(session, only_competition(session).id)
    assert [s.label for s in seasons if s.is_current] == ["2002-03"]
    assert len(seasons) == 3


def test_a_colliding_window_is_refused_and_the_rest_registered(session: Session) -> None:
    seed_countries(session, TESTLAND)
    apply_scope(session, declaration())
    competition = only_competition(session)
    # A season registered by hand, overlapping the window 2001-02 occupies.
    session.add(
        Season(
            competition_id=competition.id,
            label="2001-02 prov",
            year_start=2001,
            start_date=datetime.date(2001, 8, 1),
            end_date=datetime.date(2002, 5, 20),
            is_current=False,
        )
    )
    session.flush()

    report = apply_scope(session, declaration())

    assert [(r.label, r.collides_with) for r in report.refused] == [("2001-02", "2001-02 prov")]
    assert report.seasons.total == 2  # 2000-01 and 2002-03 still went through
    assert session.scalar(
        select(func.count())
        .select_from(Season)
        .where(Season.competition_id == competition.id, Season.label == "2001-02")
    ) == 1  # the one registered by the first apply is left standing


def test_a_source_without_a_stated_delay_gets_the_cautious_one(session: Session) -> None:
    seed_countries(session, TESTLAND)
    apply_scope(session, declaration())

    source = session.scalar(select(Source).where(Source.slug == "test-source"))
    assert source is not None
    assert source.rate_limit_ms == CAUTIOUS_RATE_LIMIT_MS
    assert source.rate_limit_is_assumed is True
