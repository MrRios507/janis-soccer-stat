from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from janis_soccer_stat.models import Country
from janis_soccer_stat.seeding import load_countries, seed_countries

TESTLAND = [{"name": "Testland", "fifa_code": "TST", "confederation": "UEFA"}]


def test_seeding_twice_inserts_once(session: Session) -> None:
    first = seed_countries(session, TESTLAND)
    second = seed_countries(session, TESTLAND)

    assert (first.inserted, first.updated) == (1, 0)
    assert (second.inserted, second.updated) == (0, 1)
    assert session.scalar(
        select(func.count()).select_from(Country).where(Country.name == "Testland")
    ) == 1


def test_seeding_again_refreshes_the_country(session: Session) -> None:
    seed_countries(session, TESTLAND)
    seed_countries(session, [{**TESTLAND[0], "fifa_code": "TSL"}])

    country = session.scalar(select(Country).where(Country.name == "Testland"))
    assert country is not None
    assert country.fifa_code == "TSL"


def test_shipped_countries_cover_the_five_leagues() -> None:
    countries = load_countries()

    assert {c["fifa_code"] for c in countries} == {"ENG", "ESP", "GER", "ITA", "FRA"}
    assert all(c["confederation"] == "UEFA" for c in countries)
