# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state

Increment 1, Match History, is the increment under way; `docs/vision.md` declares what each
increment delivers. Its data layer exists; nothing else does yet. A `uv`-managed Python
project lives under `src/janis_soccer_stat/`, with SQLAlchemy models in
`src/janis_soccer_stat/models/` mapping the thirteen entities of `docs/entity_model.md`, one
Alembic migration in `alembic/versions/`, and a `docker-compose.yml` running PostgreSQL 16
locally. No scraping, parsing, or prediction code exists yet. Do not invent commands beyond
the ones below — extend this section as real ones appear.

- Install dependencies: `uv sync`
- Start the local database: `docker compose up -d` (copy `.env.example` to `.env` first)
- Apply migrations: `uv run alembic upgrade head`
- After changing a model, generate a migration: `uv run alembic revision --autogenerate -m "..."`
- Run tests: `uv run pytest` (no tests written yet)
- No linter or formatter is configured yet.

PostgreSQL 16+ (C-001) and Python 3.11+ (C-002) are enforced concretely in
`docker-compose.yml` (`image: postgres:16`) and `pyproject.toml` (`requires-python`).

## What this project is

A post-match scraper and an independent football database for the five major European
men's leagues, built so that outcome probabilities for unplayed matches can be estimated
and honestly measured against the betting market.

## Method: AI Unified Process

This project follows the AI Unified Process (https://unifiedprocess.ai). Before making
product, domain, or architecture decisions, read `docs/vision.md`, `docs/requirements.md`
and `docs/entity_model.md`.

The work is delivered in increments (C-012), named in `docs/vision.md` with the requirements
and use cases each one covers. Only the current increment is specified in full: later
requirements sit at status `Deferred`, so do their use case specifications, and
`docs/entity_model.md` describes only the entities already built. Opening the next increment
is a specification pass of its own — reinstate its entities in the entity model, move its
requirements and use cases off `Deferred`, then write code. Design deferred out of the
artifacts is not lost: recover it with `git log -p docs/entity_model.md`.

1. Requirements derive from the vision. Anything absent from `docs/vision.md` is at risk
   of being dropped when a downstream artifact is regenerated — add it upstream first.
2. When requirements change, reconcile the entity model in the same pass.
3. When something is wrong, edit the specification and regenerate. Do not patch code and
   leave the spec behind.
4. Requirement identifiers (FR-, NFR-, C-) are the traceability spine. Never renumber or
   reuse them. Retire a requirement by setting its Status to `Rejected` or `Deferred`.
5. Do not implement a use case before its `UC-*.md` specification exists.
6. The diagram precedes the specifications. `use-case-spec` takes each `UC-XXX` id and
   name verbatim from `docs/use_cases.puml`; a spec written without a diagram entry is
   orphaned. Filenames are `UC-XXX-<kebab-case of the diagram name>.md`.
7. Use case steps describe what the system achieves, never how. No SQL, HTTP, file
   formats, or class names — the bundled validator rejects them:

   ```bash
   python3 ~/.claude/plugins/marketplaces/ai-unified-process-marketplace/aiup-core/skills/use-case-spec/scripts/validate_use_case.py --strict docs/use_cases/UC-*.md
   ```

8. `BR-XXX` business-rule ids restart at `BR-001` in every use case file; the file is
   their namespace. Cite another file's rule as `UC-005 BR-002`.

## Document map

| File | Role |
|------|------|
| `docs/vision.md` | AIUP artifact. Mission, scope, measurable goals. Root of the chain. |
| `docs/requirements.md` | AIUP artifact. FR / NFR / Constraints catalogs. |
| `docs/entity_model.md` | AIUP artifact. Canonical data model. |
| `docs/use_cases.puml` | AIUP artifact. Actors and use cases. Owns every `UC-XXX` id and name. |
| `docs/use_cases/UC-*.md` | AIUP artifact. One specification per use case. |

`docs/` holds AIUP artifacts only. Implementation notes belong in code or in this file,
never as loose documents beside the specifications, where they drift out of sync.


## Language rule

Every AIUP artifact is written in **English**. This is not cosmetic: the official
`requirements` skill enforces a hard gate that every functional requirement matches
`As a [role], I want [goal] so that [benefit]`, and `Priority`, `Status`, `Category`,
`Data Type` and `Validation Rules` are closed English vocabularies.

Commit messages, branch names and pull request descriptions are in **English**, so that
the repository history reads in the same language as the artifacts it describes.

Conversation with the user is in **Spanish**.

## Editing `entity_model.md`

The format is enforced by the AIUP `entity-model` skill. Violating it silently breaks the
tooling:

- The Mermaid diagram carries entity names and relationships **only**. No attribute blocks.
- Every entity is a `###` heading in UPPER_SNAKE_CASE, followed by one sentence, followed by
  a table with exactly these columns: `Attribute | Description | Data Type | Length/Precision | Validation Rules`.
- Data Type is a closed set: `Long`, `String`, `Integer`, `Decimal`, `Boolean`, `Date`,
  `DateTime`. Never SQL or ORM types. `Date` and `DateTime` use `-` as Length/Precision.
- Validation Rules is a closed set, one row per cell, never combined: `Primary Key, Sequence` /
  `Not Null` / `Not Null, Unique` / `Not Null, Foreign Key (TABLE.id)` / `Optional` /
  `Not Null, Min: X, Max: Y` / `Not Null, Values: A, B, C` / `Not Null, Format: Email`.
  Never `Min:` without `Max:`. Never an empty cell.
- Nullable foreign keys are marked `Optional`, with the referenced entity named in the
  Description column — the closed set has no optional-FK rule.
- Multi-column rules go in a `**Constraints:**` line after the table.

## Domain invariants

These are the rules that make the project work; breaking them is not caught by tests.

**The `as_of` cutoff.** (Increment 5, with the entities it introduces.) Every row in
`MATCH_FEATURES` and `PREDICTIONS` carries `as_of`.
Computation may read only matches kicking off before it and odds recorded before it. This is
the sole defense against data leakage, which is what produces a model scoring 70% in backtest
and 48% in production. Evaluation must be temporal, never a random split.

**Statistics are stored long, not wide.** One row per team per match in `MATCH_TEAM_STATS`,
never `home_shots`/`away_shots` columns. Goals live only in `MATCHES`; join, do not duplicate.

**Collection is idempotent.** Every write is an upsert keyed on a uniqueness constraint.
Reruns are normal and must never duplicate rows. In increment 1 a match is keyed on its
season and its home and away teams (UC-001 BR-001); a publisher's own reference for it
arrives with the external identifier mapping of increment 3.

**Raw documents are retained.** Parsers will be wrong and the error will surface months
later. Reprocess from `RAW_DOCUMENTS`; never re-request the source to fix a parse bug.

**Team name matching never guesses.** Below the confidence threshold, a match is held for
manual review. One wrongly mapped team silently corrupts the entire history of two clubs.

**xG is derived from shots, not ingested pre-aggregated**, where the source exposes shot-level
data, so `SHOTS` and `MATCH_TEAM_STATS.xg` must agree within a source. Both arrive with
increment 3; increment 1 stores no expected goals at all rather than a pre-aggregated one.

## Data sources

Three free sources, each with a distinct job. They complement rather than compete. Increment
1 collects from football-data.co.uk alone; Understat arrives with increment 3 and FBref with
increment 4.

| Source | Job | Covers | Suggested `rate_limit_ms` |
|---|---|---|---|
| football-data.co.uk | Results, odds, basic stats | ~1993 onward | 0 (plain file download) |
| Understat | Shot-level expected goals | Big five, 2014-15 onward | 2000 |
| FBref | Players, lineups, advanced team stats | Advanced stats ~2017-18 onward | 6000 |

Parsing traps, each of which costs an afternoon if unknown:

- **FBref** hides most tables inside HTML comments (`<!-- ... -->`). Parsing the document
  directly finds nothing and looks like the page changed. Extract the comments, then parse
  their contents.
- **FBref** rate-limits strictly and actively; exceeding it earns a temporary block. Check
  its current bot policy before a bulk run and prefer slower.
- **Understat** ships its data hex-escaped inside a `<script>`, as
  `JSON.parse('\x7B\x22id\x22...')`. Unescape before parsing.
- **football-data.co.uk** marks closing odds with a **`C` prefix**: `B365H` is Bet365's
  opening home price, `B365CH` the closing one. Only the closing price is the benchmark.
  `MaxC` and `AvgC` (market maximum and average at close) are usually better references
  than any single operator. League codes: `E0`, `SP1`, `D1`, `I1`, `F1`.

Which source feeds what: football-data fills matches, odds and basic team stats; Understat
fills shots, from which `MATCH_TEAM_STATS.xg` is summed; FBref fills players, lineups,
venues, referees and the non-shot team stats. `MATCH_TEAM_STATS` is therefore written by
more than one source, which is why every row names its own.

To convert odds to probabilities, remove the operator's margin:
`p = (1 / price) / sum of (1 / price) over the three outcomes`. Score with log loss, never
accuracy — accuracy rewards always naming the favourite.

Two indexes carry the whole workload, and both already exist: matches is indexed on
`(home_team_id, kickoff_utc)` and `(away_team_id, kickoff_utc)`, which recent-form
computation hits constantly, and `team_aliases.normalized` carries a trigram index, which
backs team name resolution and needs the `pg_trgm` extension the migration creates.

First model should be Dixon-Coles or bivariate Poisson over expected goals — interpretable,
trains on little data, and a fair baseline before anything heavier.

## Scraping conduct

Sources are free and rate-limited, and their terms tolerate slow personal use at best.
One sequential worker, never parallel, honoring `SOURCES.rate_limit_ms`. Collected data is
personal-use only and must not be redistributed (C-007).
