"""Test fixtures.

These tests need PostgreSQL, because everything they check — upserts on a
conflict target, partial indexes, check constraints — is the database doing the
work. Each test runs inside a transaction that is rolled back afterwards, so the
local database is left exactly as it was found, and they are skipped rather than
failed when no database is reachable.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from janis_soccer_stat.db import get_engine


@pytest.fixture
def session() -> Iterator[Session]:
    try:
        engine = get_engine()
        connection = engine.connect()
    except (RuntimeError, OperationalError) as error:
        pytest.skip(f"no database available: {error}")

    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
