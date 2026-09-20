# Use Case: Collect Team Statistics

## Overview

**Use Case ID:** UC-003  
**Use Case Name:** Collect Team Statistics  
**Primary Actor:** Data Engineer  
**Goal:** Bring the advanced team statistics of every match of a season into the database so that the model has variables that do not derive from shots  
**Status:** Deferred

## Preconditions

- The league and the season are registered as a known competition and season
- The publisher of the advanced statistics is registered as a known source
- The matches of the season are already stored

## Main Success Scenario

1. Data Engineer requests statistics collection for one league and one season.
2. System confirms that the league, the season and the publisher are known.
3. System opens a collection run for the requested league and season.
4. System obtains the list of matches the publisher offers for the season.
5. System waits for the minimum interval the publisher requires between requests.
6. System obtains the statistics of the next match.
7. System retains the obtained records in their original form.
8. System identifies the two teams of the match from the published names.
9. System binds the published match to a match already stored.
10. System records the statistics as one entry per team per match, noting which publisher reported them.
11. System records the stadium and the head referee of the match when the publisher states them.
12. System repeats from step 5 until every match of the season has been processed.
13. System closes the collection run, reporting how many matches were processed.
14. Data Engineer confirms that the season carries advanced statistics.

## Alternative Flows

### A1: Match Not Stored

**Trigger:** The published match cannot be bound to any stored match (step 9)  
**Flow:**

1. System sets the match aside for manual review without storing its statistics.
2. Use case continues at step 12.

### A2: Publisher Refuses Further Requests

**Trigger:** The publisher stops answering because too many requests were made (step 6)  
**Flow:**

1. System stops requesting and closes the collection run as partial.
2. System records the match at which it stopped so the run can be resumed.
3. Use case ends.

### A3: Publisher Reports Only Some Statistics

**Trigger:** The publisher offers a narrower set of statistics than expected (step 10)  
**Flow:**

1. System stores the statistics that were reported and leaves the rest empty.
2. System notes the absent statistics so that they appear as coverage gaps.
3. Use case continues at step 12.

### A4: Statistics Already Collected From Another Publisher

**Trigger:** Another publisher already reported statistics for the match (step 10)  
**Flow:**

1. System stores the new entry alongside the existing one, each carrying its own publisher.
2. Use case continues at step 12.

## Postconditions

### Success Postconditions

- Every match of the season for which statistics were published carries one entry per team, each naming the publisher it came from
- Stadium and referee are stored for the matches where the publisher stated them
- The obtained records are retained in their original form and can be interpreted again without contacting the publisher
- The collection run is closed as successful, carrying the count of matches processed

### Failure Postconditions

- Statistics stored by earlier runs remain unchanged
- The collection run is closed as failed or partial, carrying the reason and the point at which it stopped
- Matches that could not be bound remain set aside for manual review and carry no statistics

## Business Rules

### BR-001: Statistics Carry Their Publisher

Every stored entry names the publisher that reported it. Two publishers may describe the same match differently, and keeping both makes the disagreement visible instead of hiding it behind whichever was collected last.

### BR-002: Absent Statistics Are Empty, Not Zero

A statistic the publisher does not report is left empty. Recording it as zero would be indistinguishable from a genuine zero and would silently distort any average computed later.

### BR-003: Goals Are Never Stored Here

Goals belong to the match itself. This use case never writes them, so that the score and the statistics can never disagree.

### BR-004: One Request At A Time

Requests to a publisher are made one after another, never in parallel, always separated by at least the interval that publisher declares.
