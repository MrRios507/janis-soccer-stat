# Use Case: Derive Player Absences

## Overview

**Use Case ID:** UC-013  
**Use Case Name:** Derive Player Absences  
**Primary Actor:** Modeler  
**Goal:** Work out when a player was unavailable by noticing that he stopped appearing in his team's squads, so that an absence signal exists without any publisher of injuries  
**Status:** Deferred

## Preconditions

- Lineups are stored for the team and period in question
- The spells binding players to the team are stored

## Main Success Scenario

1. Modeler asks for absences to be derived for a team over a period.
2. System establishes which players were regular members of the squad before the period.
3. System walks the team's matches of the period in order.
4. System notes each match in which a regular member appears in no squad.
5. System groups a player's consecutive absences into a single period of unavailability.
6. System records each period, marking it as worked out from absence rather than reported by anyone.
7. System reports how many periods were derived.
8. Modeler confirms that the team's history carries an absence signal.

## Alternative Flows

### A1: Lineups Missing For A Match

**Trigger:** The match carries no stored lineup at all (step 4)  
**Flow:**

1. System passes over the match without treating anyone as absent.
2. Use case continues at step 5.

### A2: Player Left The Team

**Trigger:** The absence runs to the end of the player's spell at the team (step 5)  
**Flow:**

1. System treats the absence as a departure rather than unavailability.
2. System records no period of unavailability.
3. Use case continues at step 6.

### A3: Absence Too Short To Mean Anything

**Trigger:** The player missed fewer consecutive matches than the threshold (step 5)  
**Flow:**

1. System treats the absence as ordinary squad rotation.
2. System records no period of unavailability.
3. Use case continues at step 6.

### A4: Unavailability Already Reported

**Trigger:** A reported period already covers the same player and dates (step 6)  
**Flow:**

1. System keeps the reported period and records no derived one.
2. Use case continues at step 7.

## Postconditions

### Success Postconditions

- Stretches in which a regular squad member stopped appearing are recorded as periods of unavailability
- Each derived period is marked as worked out from absence, so it can be told apart from a reported one
- Matches with no stored lineup produced no absences
- Reported periods of unavailability are unchanged

### Failure Postconditions

- No period of unavailability is recorded
- Periods recorded earlier are unchanged

## Business Rules

### BR-001: Derived Is Always Marked As Derived

A period worked out from absence is recorded as such. It is weaker evidence than a reported one, and a model that cannot tell them apart would treat a guess as a fact.

### BR-002: A Derived Absence Cannot Forecast A Future Match

This signal only ever describes the past, because it is read from squads that have already been named. For a match not yet played there is no squad to read, so a forecast can use at most the recent availability of the usual starters. This is a real limit of working without a publisher of injuries, not something to be worked around.

### BR-003: A Missing Lineup Is Not An Absence

When no squad was stored for a match, nobody is treated as absent. Otherwise a gap in collection would appear as an entire squad falling injured at once.

### BR-004: One Match Out Is Rotation

A single missed match is ordinary rotation. Only a run of consecutive absences is recorded as unavailability.

### BR-005: A Reported Period Outranks A Derived One

Where something is reported for a player and dates, the derived period is not recorded. The two would otherwise double count the same absence.
