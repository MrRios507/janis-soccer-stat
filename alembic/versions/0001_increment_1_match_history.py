"""increment 1: match history schema

Creates the thirteen entities declared in docs/entity_model.md for increment 1:
the reference data, the competition calendar, the matches with their per-team
statistics, and the collection plumbing that keeps a run auditable and its
documents reinterpretable.

Revision ID: 0001_increment_1
Revises:
Create Date: 2026-09-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_increment_1"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Trigram similarity backs alias matching; the team_aliases index needs it.
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.create_table('countries',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('iso3', sa.String(length=3), nullable=False),
    sa.Column('confederation', sa.String(length=20), nullable=False),
    sa.CheckConstraint("confederation IN ('UEFA','CONMEBOL','CONCACAF','CAF','AFC','OFC')", name=op.f('ck_countries_confederation_valid')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_countries')),
    sa.UniqueConstraint('iso3', name=op.f('uq_countries_iso3')),
    sa.UniqueConstraint('name', name=op.f('uq_countries_name'))
    )
    op.create_table('sources',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('slug', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('base_url', sa.String(length=200), nullable=False),
    sa.Column('rate_limit_ms', sa.Integer(), nullable=False),
    sa.Column('rate_limit_is_assumed', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sources')),
    sa.UniqueConstraint('slug', name=op.f('uq_sources_slug'))
    )
    op.create_table('competitions',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('format', sa.String(length=20), nullable=False),
    sa.Column('scope', sa.String(length=20), nullable=False),
    sa.Column('country_id', sa.BigInteger(), nullable=True),
    sa.Column('confederation', sa.String(length=20), nullable=True),
    sa.Column('tier', sa.Integer(), nullable=True),
    sa.Column('gender', sa.String(length=10), nullable=False),
    sa.Column('is_collected', sa.Boolean(), nullable=False),
    sa.CheckConstraint("format IN ('league','cup','group_knockout')", name=op.f('ck_competitions_format_valid')),
    sa.CheckConstraint("gender IN ('male','female')", name=op.f('ck_competitions_gender_valid')),
    sa.CheckConstraint("scope IN ('domestic','continental','international')", name=op.f('ck_competitions_scope_valid')),
    sa.ForeignKeyConstraint(['country_id'], ['countries.id'], name=op.f('fk_competitions_country_id_countries')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_competitions'))
    )
    op.create_table('referees',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('country_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['country_id'], ['countries.id'], name=op.f('fk_referees_country_id_countries')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_referees'))
    )
    op.create_table('venues',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('country_id', sa.BigInteger(), nullable=True),
    sa.Column('capacity', sa.Integer(), nullable=True),
    sa.Column('latitude', sa.Numeric(precision=9, scale=6), nullable=True),
    sa.Column('longitude', sa.Numeric(precision=9, scale=6), nullable=True),
    sa.Column('altitude_m', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['country_id'], ['countries.id'], name=op.f('fk_venues_country_id_countries')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_venues'))
    )
    op.create_table('teams',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('short_name', sa.String(length=50), nullable=True),
    sa.Column('country_id', sa.BigInteger(), nullable=True),
    sa.Column('founded_year', sa.Integer(), nullable=True),
    sa.Column('is_national_team', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['country_id'], ['countries.id'], name=op.f('fk_teams_country_id_countries')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_teams'))
    )
    op.create_table('scrape_runs',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('source_id', sa.BigInteger(), nullable=False),
    sa.Column('target', sa.String(length=200), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('items_found', sa.Integer(), nullable=True),
    sa.Column('items_upserted', sa.Integer(), nullable=True),
    sa.Column('items_failed', sa.Integer(), nullable=True),
    sa.Column('resume_point', sa.String(length=200), nullable=True),
    sa.Column('error', sa.String(length=2000), nullable=True),
    sa.CheckConstraint("status <> 'partial' OR resume_point IS NOT NULL", name=op.f('ck_scrape_runs_partial_has_resume_point')),
    sa.CheckConstraint("status <> 'running' OR finished_at IS NULL", name=op.f('ck_scrape_runs_running_has_no_finish')),
    sa.CheckConstraint("status IN ('running','ok','failed','partial','abandoned')", name=op.f('ck_scrape_runs_status_valid')),
    sa.CheckConstraint('finished_at IS NULL OR finished_at > started_at', name=op.f('ck_scrape_runs_finish_after_start')),
    sa.ForeignKeyConstraint(['source_id'], ['sources.id'], name=op.f('fk_scrape_runs_source_id_sources')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_scrape_runs'))
    )
    op.create_index('ix_scrape_runs_one_running_per_source_target', 'scrape_runs', ['source_id', 'target'], unique=True, postgresql_where=sa.text("status = 'running'"))
    op.create_table('team_aliases',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('team_id', sa.BigInteger(), nullable=False),
    sa.Column('alias', sa.String(length=100), nullable=False),
    sa.Column('normalized', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name=op.f('fk_team_aliases_team_id_teams')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_team_aliases')),
    sa.UniqueConstraint('team_id', 'normalized', name=op.f('uq_team_aliases_team_id_normalized'))
    )
    op.create_index('ix_team_aliases_normalized_trgm', 'team_aliases', ['normalized'], unique=False, postgresql_using='gin', postgresql_ops={'normalized': 'gin_trgm_ops'})
    op.create_table('seasons',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('competition_id', sa.BigInteger(), nullable=False),
    sa.Column('label', sa.String(length=20), nullable=False),
    sa.Column('year_start', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('num_teams', sa.Integer(), nullable=True),
    sa.Column('is_current', sa.Boolean(), nullable=False),
    sa.CheckConstraint('end_date IS NULL OR start_date IS NULL OR end_date > start_date', name=op.f('ck_seasons_end_after_start')),
    sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], name=op.f('fk_seasons_competition_id_competitions')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_seasons')),
    sa.UniqueConstraint('competition_id', 'label', name=op.f('uq_seasons_competition_id_label'))
    )
    op.create_table('raw_documents',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('scrape_run_id', sa.BigInteger(), nullable=False),
    sa.Column('url', sa.String(length=500), nullable=False),
    sa.Column('content_hash', sa.String(length=64), nullable=False),
    sa.Column('status_code', sa.Integer(), nullable=False),
    sa.Column('payload', sa.Text(), nullable=False),
    sa.Column('attempts', sa.Integer(), nullable=False),
    sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('parsed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('reading_version', sa.String(length=20), nullable=True),
    sa.Column('parse_error', sa.String(length=2000), nullable=True),
    sa.CheckConstraint('parsed_at IS NULL OR reading_version IS NOT NULL', name=op.f('ck_raw_documents_parsed_requires_reading_version')),
    sa.ForeignKeyConstraint(['scrape_run_id'], ['scrape_runs.id'], name=op.f('fk_raw_documents_scrape_run_id_scrape_runs')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_raw_documents')),
    sa.UniqueConstraint('content_hash', name=op.f('uq_raw_documents_content_hash'))
    )
    op.create_table('held_records',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('scrape_run_id', sa.BigInteger(), nullable=False),
    sa.Column('source_id', sa.BigInteger(), nullable=False),
    sa.Column('held_kind', sa.String(length=20), nullable=False),
    sa.Column('published_value', sa.String(length=200), nullable=False),
    sa.Column('context', sa.String(length=500), nullable=True),
    sa.Column('candidates', sa.String(length=2000), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('resolved_ref', sa.BigInteger(), nullable=True),
    sa.Column('held_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint("(status <> 'resolved' OR (resolved_ref IS NOT NULL AND resolved_at IS NOT NULL)) AND (status <> 'pending' OR (resolved_ref IS NULL AND resolved_at IS NULL))", name=op.f('ck_held_records_resolution_fields_match_status')),
    sa.CheckConstraint("held_kind IN ('team')", name=op.f('ck_held_records_held_kind_valid')),
    sa.CheckConstraint("status IN ('pending','resolved','discarded')", name=op.f('ck_held_records_status_valid')),
    sa.ForeignKeyConstraint(['scrape_run_id'], ['scrape_runs.id'], name=op.f('fk_held_records_scrape_run_id_scrape_runs')),
    sa.ForeignKeyConstraint(['source_id'], ['sources.id'], name=op.f('fk_held_records_source_id_sources')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_held_records'))
    )
    op.create_index('ix_held_records_unique_while_pending', 'held_records', ['source_id', 'held_kind', 'published_value'], unique=True, postgresql_where=sa.text("status = 'pending'"))
    op.create_table('matches',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('season_id', sa.BigInteger(), nullable=False),
    sa.Column('home_team_id', sa.BigInteger(), nullable=False),
    sa.Column('away_team_id', sa.BigInteger(), nullable=False),
    sa.Column('venue_id', sa.BigInteger(), nullable=True),
    sa.Column('referee_id', sa.BigInteger(), nullable=True),
    sa.Column('kickoff_utc', sa.DateTime(timezone=True), nullable=False),
    sa.Column('local_date', sa.Date(), nullable=False),
    sa.Column('stage', sa.String(length=30), nullable=True),
    sa.Column('round', sa.String(length=30), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('neutral_venue', sa.Boolean(), nullable=False),
    sa.Column('home_score', sa.Integer(), nullable=True),
    sa.Column('away_score', sa.Integer(), nullable=True),
    sa.Column('home_score_ht', sa.Integer(), nullable=True),
    sa.Column('away_score_ht', sa.Integer(), nullable=True),
    sa.Column('home_score_et', sa.Integer(), nullable=True),
    sa.Column('away_score_et', sa.Integer(), nullable=True),
    sa.Column('home_pens', sa.Integer(), nullable=True),
    sa.Column('away_pens', sa.Integer(), nullable=True),
    sa.Column('attendance', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_scraped_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint("status <> 'finished' OR (home_score IS NOT NULL AND away_score IS NOT NULL)", name=op.f('ck_matches_finished_has_scores')),
    sa.CheckConstraint("status IN ('scheduled','live','finished','postponed','cancelled')", name=op.f('ck_matches_status_valid')),
    sa.CheckConstraint('(home_score_et IS NULL OR home_score IS NOT NULL) AND (away_score_et IS NULL OR away_score IS NOT NULL)', name=op.f('ck_matches_extra_time_requires_regular_time')),
    sa.CheckConstraint('home_team_id <> away_team_id', name=op.f('ck_matches_home_away_different')),
    sa.ForeignKeyConstraint(['away_team_id'], ['teams.id'], name=op.f('fk_matches_away_team_id_teams')),
    sa.ForeignKeyConstraint(['home_team_id'], ['teams.id'], name=op.f('fk_matches_home_team_id_teams')),
    sa.ForeignKeyConstraint(['referee_id'], ['referees.id'], name=op.f('fk_matches_referee_id_referees')),
    sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], name=op.f('fk_matches_season_id_seasons')),
    sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], name=op.f('fk_matches_venue_id_venues')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_matches')),
    sa.UniqueConstraint('season_id', 'home_team_id', 'away_team_id', name=op.f('uq_matches_season_id_home_team_id_away_team_id'))
    )
    op.create_index('ix_matches_away_team_kickoff', 'matches', ['away_team_id', 'kickoff_utc'], unique=False)
    op.create_index('ix_matches_home_team_kickoff', 'matches', ['home_team_id', 'kickoff_utc'], unique=False)
    op.create_table('match_team_stats',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('match_id', sa.BigInteger(), nullable=False),
    sa.Column('team_id', sa.BigInteger(), nullable=False),
    sa.Column('source_id', sa.BigInteger(), nullable=False),
    sa.Column('is_home', sa.Boolean(), nullable=False),
    sa.Column('shots', sa.Integer(), nullable=True),
    sa.Column('shots_on_target', sa.Integer(), nullable=True),
    sa.Column('woodwork', sa.Integer(), nullable=True),
    sa.Column('corners', sa.Integer(), nullable=True),
    sa.Column('offsides', sa.Integer(), nullable=True),
    sa.Column('fouls', sa.Integer(), nullable=True),
    sa.Column('yellow_cards', sa.Integer(), nullable=True),
    sa.Column('red_cards', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['matches.id'], name=op.f('fk_match_team_stats_match_id_matches')),
    sa.ForeignKeyConstraint(['source_id'], ['sources.id'], name=op.f('fk_match_team_stats_source_id_sources')),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name=op.f('fk_match_team_stats_team_id_teams')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_match_team_stats')),
    sa.UniqueConstraint('match_id', 'team_id', 'source_id', name=op.f('uq_match_team_stats_match_id_team_id_source_id'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('match_team_stats')
    op.drop_index('ix_matches_away_team_kickoff', table_name='matches')
    op.drop_index('ix_matches_home_team_kickoff', table_name='matches')
    op.drop_table('matches')
    op.drop_index('ix_held_records_unique_while_pending', table_name='held_records')
    op.drop_table('held_records')
    op.drop_table('raw_documents')
    op.drop_table('seasons')
    op.drop_index('ix_team_aliases_normalized_trgm', table_name='team_aliases')
    op.drop_table('team_aliases')
    op.drop_index('ix_scrape_runs_one_running_per_source_target', table_name='scrape_runs')
    op.drop_table('scrape_runs')
    op.drop_table('teams')
    op.drop_table('venues')
    op.drop_table('referees')
    op.drop_table('competitions')
    op.drop_table('sources')
    op.drop_table('countries')
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
