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

## Constraints

- Only free, publicly accessible data sources may be used.
- Sources impose request limits that govern how long collection takes.
- Collected data is for personal use and must not be redistributed.
- Expected goals availability is limited to the seasons and leagues covered by
  the corresponding source.
- The project is developed by one person without full-time dedication.
- Execution happens on a local machine, with no cloud infrastructure.

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
