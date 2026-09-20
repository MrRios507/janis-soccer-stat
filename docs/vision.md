# Vision: janis-soccer-stat

## Mission

Build an independent football data source, fed by post-match collection from free
public sources, and use it to estimate the outcome probabilities of matches not
yet played. The system replaces reliance on third-party data with a verifiable,
reproducible history against which it is possible to honestly measure whether a
model adds information beyond what the betting market already prices in.

## Target users

- **Sports data analyst**: needs a consistent and complete match history with
  advanced statistics, queryable without depending on the availability of an
  external service.
- **Modeler**: needs to generate predictive features free of temporal
  contamination and to evaluate models against an objective reference.
- **Data engineer**: needs collection to be repeatable, auditable, and able to
  recover from failure without losing work already done.
- **Operator**: needs to run the periodic update without manual intervention and
  to detect when a source has changed its format.

In practice all four roles are held by the same person; they are distinguished
because each places different demands on the system.

## Goals

- Hold at least 20000 matches with expected goals from the five major European
  leagues from the 2014-15 season onward.
- Cover at least 95 percent of matches loaded from the 2005-06 season onward with
  closing odds.
- Reach a log loss on the 1X2 market no higher than 1.02 under temporal
  validation.
- Keep the model log loss within 0.02 of the closing odds log loss on the same
  evaluation set.
- Complete the weekly data update unattended.

## Scope

### In scope

- Declaration of which competitions and seasons the system collects, which sources
  feed them, and what each of those sources actually publishes.
- Loading historical results, basic statistics and odds from published files.
- Post-match collection of individual shots with expected goals.
- Post-match collection of advanced team statistics, lineups and minutes played.
- Consolidation of heterogeneous sources onto a single set of entities.
- Retention of the original document of every download for reprocessing.
- Resumption of interrupted collections and retry of transient failures.
- Manual review of ambiguous entity matches before they enter the history.
- Reporting of data coverage gaps per league and season.
- Registration of scheduled matches before they are played.
- Generation of predictive features with an explicit cutoff instant.
- Training, registration and temporal evaluation of 1X2 outcome models.
- Comparison of predictions against the probability implied by the market.

### Out of scope

- Live or in-play match data.
- Automated bet placement, bankroll management or stake sizing.
- Betting recommendations offered to third parties.
- Women's, youth and lower-tier competitions.
- Transfer markets and player valuation.
- A public web interface or any service reachable from outside the local machine.
- Injuries and lineups confirmed before kickoff, for lack of a free source.
- Paid data sources.

## Delivery increments

The scope above is the destination, not the first delivery. It is built in increments, each
one a slice that runs from end to end and is worth having on its own. Only the current
increment is specified in full: a requirement or use case belonging to a later one is held
at status `Deferred`, and the entity model describes only what the current increment has
built. Deferred design is not lost, it is simply not yet part of the system, and it is
reinstated in the pass that opens its increment.

### Increment 1: Match history

Declare the competitions, seasons and publisher the system works on; load the published
results and basic team statistics of a season; bind the published team names to known teams
and hold whatever cannot be bound with confidence; leave every run auditable and every
document reinterpretable without contacting the publisher. Delivers a chronological match
history per team, queryable on its own.

Requirements FR-001, FR-005, FR-006, FR-007, FR-009, FR-010, FR-011, FR-012, FR-014,
FR-022, FR-026, FR-027, NFR-001, NFR-003, NFR-005, NFR-008, NFR-009, NFR-010, NFR-011.
Use cases UC-015, UC-001, UC-005, UC-014, UC-007, UC-006.

### Increment 2: Market reference

Read the closing prices quoted for every match already loaded, and the probability they
imply, out of the documents increment 1 retained. No publisher is contacted, which is the
first real proof that retention and reinterpretation work.

Requirements FR-013. Extends UC-001; adds no use case.

### Increment 3: Expected goals

Add a second publisher, shot by shot, and with it the need to recognise the same team and
the same match under two different publishers' own references. Expected goals are summed
from the shots rather than taken pre-aggregated.

Requirements FR-002, FR-008, NFR-004. Use case UC-002.

### Increment 4: Advanced statistics and squads

Add the publisher of players, lineups, minutes played and the team statistics that do not
derive from shots, and report what is covered and what is missing per league and season.

Requirements FR-003, FR-004, FR-023, FR-024, FR-028, NFR-006. Use cases UC-003, UC-004,
UC-008.

### Increment 5: Prediction

Compute features under an explicit cutoff instant, train and register models, evaluate them
temporally against the closing prices, and issue probabilities for matches not yet played.

Requirements FR-015, FR-016, FR-017, FR-018, FR-019, FR-020, FR-021, FR-025, NFR-002,
NFR-007. Use cases UC-009, UC-010, UC-011, UC-012, UC-013.

## Constraints

- Only free, publicly accessible data sources may be used.
- Sources impose request limits that govern how long collection takes.
- Collected data is for personal use and must not be redistributed.
- Expected goals availability is limited to the seasons and leagues covered by
  the corresponding source.
- The project is developed by one person without full-time dedication.
- Execution happens on a local machine, with no cloud infrastructure.
- Work is delivered in increments; nothing is built before the increment that declares it.

## Success measures

- Weekly collection completes without manual intervention for eight consecutive
  weeks.
- Two evaluation runs with the same configuration produce identical metrics.
- Every prediction issued can be traced back to the model, the feature set and
  the cutoff instant that produced it.
- An automated check confirms that no training feature absorbs information later
  than its cutoff instant.
- Correcting a parsing error across a full season requires no request to the
  original source.
