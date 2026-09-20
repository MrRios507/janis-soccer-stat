"""Database access: one engine for the process, sessions on top of it.

The URL is read from the environment exactly as alembic/env.py reads it, so it
lives in .env and nowhere else (NFR-010).
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def database_url() -> str:
    load_dotenv()
    try:
        return os.environ["DATABASE_URL"]
    except KeyError:
        raise RuntimeError(
            "DATABASE_URL is not set. Copy .env.example to .env and start the "
            "database with `docker compose up -d`."
        ) from None


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(database_url())


@lru_cache(maxsize=1)
def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


@contextmanager
def session_scope() -> Iterator[Session]:
    """A session that commits on success and rolls back on any failure.

    Everything a command writes lands together or not at all, which is what
    keeps a failed run from leaving a half-declared scope behind.
    """
    session = get_sessionmaker()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
