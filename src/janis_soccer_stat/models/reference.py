from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    # Football associations, not ISO 3166: England, Scotland and Wales are
    # countries here and have no ISO alpha-3 code of their own.
    fifa_code: Mapped[str] = mapped_column(String(3), nullable=False, unique=True)
    confederation: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "confederation IN ('UEFA','CONMEBOL','CONCACAF','CAF','AFC','OFC')",
            name="confederation_valid",
        ),
    )


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    country_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("countries.id"))
    capacity: Mapped[Optional[int]] = mapped_column(Integer)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6))
    altitude_m: Mapped[Optional[int]] = mapped_column(Integer)


class Referee(Base):
    __tablename__ = "referees"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("countries.id"))


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_url: Mapped[str] = mapped_column(String(200), nullable=False)
    rate_limit_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    rate_limit_is_assumed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
