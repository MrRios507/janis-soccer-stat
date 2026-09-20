"""country code and competition natural key

COUNTRIES.iso3 becomes fifa_code: England, Scotland and Wales are countries in
this domain and have no ISO 3166 alpha-3 code, so the football association code
is the only one that covers every country the system collects.

COMPETITIONS gains a natural key, which UC-015 A1 needs to update a competition
already declared instead of registering a second one.

Revision ID: 0002_competition_key
Revises: 0001_increment_1
Create Date: 2026-09-19

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0002_competition_key"
down_revision: Union[str, Sequence[str], None] = "0001_increment_1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("countries", "iso3", new_column_name="fifa_code")
    op.drop_constraint(op.f("uq_countries_iso3"), "countries", type_="unique")
    op.create_unique_constraint(op.f("uq_countries_fifa_code"), "countries", ["fifa_code"])
    op.create_unique_constraint(
        op.f("uq_competitions_name_country_id"), "competitions", ["name", "country_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("uq_competitions_name_country_id"), "competitions", type_="unique")
    op.drop_constraint(op.f("uq_countries_fifa_code"), "countries", type_="unique")
    op.alter_column("countries", "fifa_code", new_column_name="iso3")
    op.create_unique_constraint(op.f("uq_countries_iso3"), "countries", ["iso3"])
