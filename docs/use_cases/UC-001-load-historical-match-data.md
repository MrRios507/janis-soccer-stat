# Use Case: Load Historical Match Data

## Overview

**Use Case ID:** UC-001  
**Use Case Name:** Load Historical Match Data  
**Primary Actor:** Data Engineer  
**Goal:** Bring a full season of published match results and basic team statistics into the database so that the season becomes available for analysis  
**Status:** Draft

## Preconditions

- The league and the season are registered as a known competition and season
- The publisher of the historical records is registered as a known source
- No other collection run is in progress for the same league and season

## Main Success Scenario

1. Data Engineer requests the historical load for one league and one season.
2. System confirms that the league and the season are known.
3. System opens a collection run for the requested league and season.
4. System obtains the published match records for that league and season.
5. System retains the obtained records in their original form.
6. System identifies the home team and the away team of each record from the published names.
7. System records each match with its date, round and final score, updating the matches it already knows.
8. System records the reported team statistics as one entry per team per match.
9. System closes the collection run, reporting how many records were found and how many were stored or updated.
10. Data Engineer confirms that the season is available for analysis.

## Alternative Flows

### A1: Season Records Not Published

**Trigger:** The publisher offers no records for the requested league and season (step 4)  
**Flow:**

1. System closes the collection run as failed, stating that the season is not published.
2. System stores no match data for the season.
3. Use case ends.

### A2: Team Name Not Recognised

**Trigger:** A published team name cannot be confidently matched to a known team (step 6)  
**Flow:**

1. System sets the affected records aside for manual review.
2. System continues with the records whose teams were recognised.
3. Data Engineer resolves the set-aside team identities later.
4. Use case continues at step 7.

### A3: Season Already Loaded

**Trigger:** The season was loaded by an earlier run (step 7)  
**Flow:**

1. System updates the matches it already knows instead of creating new ones.
2. System reports how many matches were updated rather than added.
3. Use case continues at step 8.

### A4: Match Without A Final Score

**Trigger:** A published record carries no final score (step 7)  
**Flow:**

1. System records the match as scheduled and leaves its score empty.
2. Use case continues at step 8.

## Postconditions

### Success Postconditions

- Every published match of the season is stored, carrying its final score when the match was played and marked as scheduled when it was not
- The reported team statistics are stored as one entry per team per match
- The obtained records are retained in their original form and can be interpreted again without contacting the publisher
- The collection run is closed as successful, carrying the count of records found and the count stored or updated

### Failure Postconditions

- Matches stored by earlier runs remain unchanged
- No partially interpreted season is left behind
- The collection run is closed as failed, carrying the reason
- Records whose team could not be identified remain set aside for manual review and are linked to no team

## Business Rules

### BR-001: Reloading Never Duplicates

A match that is already stored is updated in place rather than added again. The match is recognised by its season and by which team played at home against which team away, which identifies it in a league where every pair of teams meets once at each ground. A season may therefore be reloaded any number of times without changing the number of stored matches.

### BR-002: Team Identification Never Guesses

A published team name is only bound to a known team when the match is confident. Below that confidence the record is set aside for manual review. A wrongly bound team corrupts the entire history of two clubs, so an unresolved record is always preferable to a wrong one.

### BR-003: A Match Without A Result Is Not An Error

A published record with no final score describes a match that has not been played. It is stored as a scheduled match so that it can later receive a prediction.

### BR-004: Goals Are Stored Once

Goals belong to the match. They are never repeated inside the team statistics, so that the two can never disagree.
