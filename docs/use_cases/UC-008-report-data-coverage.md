# Use Case: Report Data Coverage

## Overview

**Use Case ID:** UC-008  
**Use Case Name:** Report Data Coverage  
**Primary Actor:** Analyst  
**Goal:** See how much of each statistic is actually present per league and season, so that gaps in the data are known before they are mistaken for findings in a model  
**Status:** Deferred

## Preconditions

- At least one league and season hold stored matches

## Main Success Scenario

1. Analyst asks for a coverage report over a set of leagues and seasons.
2. System counts the matches stored for each league and season.
3. System counts, for each statistic, how many of those matches carry a value for it.
4. System expresses each count as a share of the matches of that league and season.
5. System lists the played matches that carry no statistics at all.
6. System presents the report grouped by league and season.
7. Analyst identifies which gaps are worth filling before modelling.

## Alternative Flows

### A1: Season Holds No Matches

**Trigger:** A requested season has no stored matches (step 2)  
**Flow:**

1. System reports the season as empty rather than leaving it out of the report.
2. Use case continues at step 6.

### A2: Statistic Never Offered By Any Publisher

**Trigger:** A statistic was never published for the league and season (step 3)  
**Flow:**

1. System marks the statistic as unavailable at the publisher rather than absent from the database.
2. Use case continues at step 4.

### A3: No Gaps Found

**Trigger:** Every played match carries statistics (step 5)  
**Flow:**

1. System states that the range is complete.
2. Use case continues at step 6.

### A4: Analyst Requests Recollection

**Trigger:** Analyst decides the listed incomplete matches should be collected again (step 7)  
**Flow:**

1. System hands the list of incomplete matches to a collection run so that only those are requested.
2. Use case ends.

## Postconditions

### Success Postconditions

- The share of matches carrying each statistic is known for every requested league and season
- Played matches carrying no statistics are listed individually and can be collected again selectively
- Statistics that no publisher offers are distinguished from statistics that were simply not collected
- The stored data is unchanged by the report

### Failure Postconditions

- No report is produced
- The stored data is unchanged

## Business Rules

### BR-001: Absent And Unavailable Are Different

A statistic no publisher ever offered is reported as unavailable, not as a gap. Treating the two alike would send the Analyst chasing data that does not exist, and would hide the gaps that can actually be closed.

### BR-002: Only Played Matches Can Have Gaps

A scheduled match carries no statistics because it has not been played. It is never counted as incomplete.

### BR-003: Coverage Is Measured Per League And Season

A single overall percentage hides the truth, because coverage varies sharply between leagues and across seasons. The report is always broken down.

### BR-004: The Report Reads, It Never Writes

Producing the report changes nothing. It may be asked for at any time, including while a collection is running.
