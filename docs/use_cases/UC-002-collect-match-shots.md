# Use Case: Collect Match Shots

## Overview

**Use Case ID:** UC-002  
**Use Case Name:** Collect Match Shots  
**Primary Actor:** Data Engineer  
**Goal:** Bring the individual shots of every match of a season into the database so that each team's expected goals are derived from its own shots rather than taken already aggregated  
**Status:** Deferred

## Preconditions

- The league and the season are registered as a known competition and season
- The publisher of the shot records is registered as a known source
- The matches of the season are already stored

## Main Success Scenario

1. Data Engineer requests shot collection for one league and one season.
2. System confirms that the league, the season and the publisher are known.
3. System opens a collection run for the requested league and season.
4. System obtains the list of matches the publisher offers for the season.
5. System waits for the minimum interval the publisher requires between requests.
6. System obtains the shot records of the next match.
7. System retains the obtained records in their original form.
8. System identifies the two teams of the match from the published names.
9. System binds the published match to a match already stored.
10. System records each shot with its minute, its position on the pitch, its scoring probability and its outcome.
11. System derives the expected goals of each team by adding up the scoring probability of the shots that team took.
12. System repeats from step 5 until every match of the season has been processed.
13. System closes the collection run, reporting how many matches were processed and how many shots were stored.
14. Data Engineer confirms that the season now carries expected goals.

## Alternative Flows

### A1: Match Not Stored

**Trigger:** The published match cannot be bound to any stored match (step 9)  
**Flow:**

1. System sets the match aside for manual review without storing its shots.
2. System notes that the season is incomplete.
3. Use case continues at step 12.

### A2: Publisher Refuses Further Requests

**Trigger:** The publisher stops answering because too many requests were made (step 6)  
**Flow:**

1. System stops requesting and closes the collection run as partial.
2. System records the match at which it stopped so the run can be resumed.
3. Use case ends.

### A3: No Shots Published For A Match

**Trigger:** The publisher offers no shot records for the match (step 6)  
**Flow:**

1. System records no shots for that match.
2. System notes the absence so that it appears as a coverage gap.
3. Use case continues at step 12.

### A4: Derived Expected Goals Disagree With The Published Total

**Trigger:** The sum of the shots differs from the team total the publisher states (step 11)  
**Flow:**

1. System stores the shots and the derived total.
2. System flags the match as inconsistent for later inspection.
3. Use case continues at step 12.

## Postconditions

### Success Postconditions

- Every match of the season for which shots were published carries its individual shots
- Each team's expected goals for those matches equal the sum of the scoring probabilities of its own shots
- The obtained records are retained in their original form and can be interpreted again without contacting the publisher
- The collection run is closed as successful, carrying the count of matches processed and shots stored

### Failure Postconditions

- Shots stored by earlier runs remain unchanged
- The collection run is closed as failed or partial, carrying the reason and the point at which it stopped
- Matches that could not be bound remain set aside for manual review and carry no shots

## Business Rules

### BR-001: Expected Goals Are Derived, Never Taken

A team's expected goals for a match are always the sum of the scoring probabilities of the shots that team took. A team total offered directly by the publisher is never stored in place of that sum, so that the shots and the total can never disagree.

### BR-002: One Request At A Time

Requests to a publisher are made one after another, never in parallel, always separated by at least the interval that publisher declares. Collecting faster than the publisher allows risks losing access to it altogether.

### BR-003: A Missing Match Is Never Invented

This use case never creates a match. A published match that is unknown to the system is set aside, because creating it here would produce a match without the result and odds that the historical load provides.

### BR-004: Recollecting Does Not Duplicate Shots

Running the collection again over a season already collected replaces the shots of each match rather than adding them a second time.
