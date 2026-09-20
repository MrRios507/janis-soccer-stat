# Use Case: Collect Lineups

## Overview

**Use Case ID:** UC-004  
**Use Case Name:** Collect Lineups  
**Primary Actor:** Data Engineer  
**Goal:** Bring the squad each team fielded in every match of a season, with the minutes each player spent on the pitch, so that historical squad availability can later be derived  
**Status:** Deferred

## Preconditions

- The league and the season are registered as a known competition and season
- The publisher of the lineups is registered as a known source
- The matches of the season are already stored

## Main Success Scenario

1. Data Engineer requests lineup collection for one league and one season.
2. System confirms that the league, the season and the publisher are known.
3. System opens a collection run for the requested league and season.
4. System obtains the list of matches the publisher offers for the season.
5. System waits for the minimum interval the publisher requires between requests.
6. System obtains the lineups of the next match.
7. System retains the obtained records in their original form.
8. System binds the published match to a match already stored.
9. System identifies each named player, registering the ones it does not yet know.
10. System records, for each player, the team he was selected for, whether he started, the position he occupied and the minutes he played.
11. System repeats from step 5 until every match of the season has been processed.
12. System closes the collection run, reporting how many matches were processed and how many players were newly registered.
13. Data Engineer confirms that the season carries lineups.

## Alternative Flows

### A1: Match Not Stored

**Trigger:** The published match cannot be bound to any stored match (step 8)  
**Flow:**

1. System sets the match aside for manual review without storing its lineups.
2. Use case continues at step 11.

### A2: Player Name Matches Several Known Players

**Trigger:** A published player name could belong to more than one known player (step 9)  
**Flow:**

1. System sets the player aside for manual review rather than choosing one.
2. System stores the rest of the lineup.
3. Use case continues at step 11.

### A3: Lineups Not Published For A Match

**Trigger:** The publisher offers no lineups for the match (step 6)  
**Flow:**

1. System records no lineup for that match.
2. System notes the absence so that it appears as a coverage gap.
3. Use case continues at step 11.

### A4: Publisher Refuses Further Requests

**Trigger:** The publisher stops answering because too many requests were made (step 6)  
**Flow:**

1. System stops requesting and closes the collection run as partial.
2. System records the match at which it stopped so the run can be resumed.
3. Use case ends.

## Postconditions

### Success Postconditions

- Every match of the season for which lineups were published carries the squad of both teams
- Each selected player carries whether he started and how many minutes he played
- Players not previously known are registered and bound to the team that fielded them
- The collection run is closed as successful, carrying the count of matches processed and players newly registered

### Failure Postconditions

- Lineups stored by earlier runs remain unchanged
- The collection run is closed as failed or partial, carrying the reason and the point at which it stopped
- Players whose identity was ambiguous remain set aside for manual review and appear in no lineup

## Business Rules

### BR-001: A Player Appears Once Per Match

A player appears at most once in a match, for one team only. A second appearance for the same match replaces the first rather than adding to it.

### BR-002: Ambiguous Players Are Never Guessed

When a published name could belong to more than one known player, the record is set aside. Binding the wrong player distorts the availability history of two squads at once.

### BR-003: An Unused Substitute Is Still A Selection

A player named in the squad who never came on is recorded with no minutes played. He was available, and availability is precisely what this use case exists to capture.

### BR-004: One Request At A Time

Requests to a publisher are made one after another, never in parallel, always separated by at least the interval that publisher declares.
