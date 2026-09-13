# Use Case: Configure Collection Scope

## Overview

**Use Case ID:** UC-015  
**Use Case Name:** Configure Collection Scope  
**Primary Actor:** Data Engineer  
**Goal:** Declare which competitions and seasons the system collects, which sources feed them and what each of those sources publishes, so that every collection knows what it is expected to work on  
**Status:** Draft

## Preconditions

- The countries the competitions belong to are registered

## Main Success Scenario

1. Data Engineer states a competition the system should cover, with how it is contested, its territorial reach and its level.
2. System registers the competition.
3. Data Engineer states the seasons of that competition to be collected, each with its label and its window of play.
4. System registers the seasons and marks the one currently being played.
5. Data Engineer states a source that publishes data for the competition, with the address it is reached at and the shortest delay it requires between requests.
6. System registers the source and records the reference under which that source identifies the competition.
7. Data Engineer states which statistics the source publishes for the competition, and from which season each became available.
8. System records what the source offers, so that anything it never publishes is not later reported as a gap.
9. System confirms that the competition, its seasons and its sources are ready to be collected.
10. Data Engineer confirms that the scope is complete.

## Alternative Flows

### A1: Competition Already Declared

**Trigger:** The competition is already registered (step 2)  
**Flow:**

1. System updates the existing competition rather than registering a second one.
2. Use case continues at step 3.

### A2: Season Overlaps One Already Declared

**Trigger:** The stated window of play overlaps another season of the same competition (step 4)  
**Flow:**

1. System refuses that season and states which one it collides with.
2. System keeps the seasons already registered.
3. Use case continues at step 5.

### A3: Source States No Required Delay

**Trigger:** The source publishes no limit on how often it may be asked (step 5)  
**Flow:**

1. System applies the most cautious delay it knows rather than none.
2. System notes that the delay was assumed and not stated by the source.
3. Use case continues at step 6.

### A4: Competition Withdrawn From Scope

**Trigger:** Data Engineer decides a competition should no longer be collected (step 1)  
**Flow:**

1. Data Engineer withdraws the competition from the scope.
2. System stops offering it for collection while keeping everything already gathered for it.
3. Use case ends.

### A5: Source Offers Nothing For The Competition

**Trigger:** The source turns out to publish nothing for the competition (step 7)  
**Flow:**

1. System records that the source offers nothing for that competition.
2. System stops pairing the two for collection.
3. Use case continues at step 9.

## Postconditions

### Success Postconditions

- The competition is registered, and each of its declared seasons carries its window of play
- Exactly one season of the competition is marked as currently being played
- Every source feeding the competition is registered with its address and its required delay
- The reference each source uses for the competition is recorded
- What each source publishes for the competition is recorded season by season
- The preconditions that the collection use cases assume now hold, so they can run

### Failure Postconditions

- No competition, season or source is registered by the attempt
- Scope declared earlier is unchanged, and what was already collected under it is untouched
- Collection use cases depending on the rejected declaration remain unable to run

## Business Rules

### BR-001: Nothing Is Collected Before It Is Declared

A collection only ever runs against a competition, season and source already declared here. Allowing collection to invent them would let a typo create a second competition silently, splitting a league's history in two.

### BR-002: Narrowing The Scope Never Discards Data

Withdrawing a competition stops future collection but keeps everything already gathered. Scope says what will be collected from now on, never what is allowed to exist.

### BR-003: Every Source Carries A Delay

A source with no stated limit is given the most cautious delay rather than none. Being blocked by a source costs far more than collecting slowly, and a source that has not published a limit still has one.

### BR-004: What A Source Never Offers Is Recorded As Such

A statistic a source does not publish is recorded as not offered, not left unsaid. This is what allows a coverage report to separate data still to be collected from data that will never exist.

### BR-005: Seasons Of One Competition Do Not Overlap

Two seasons of the same competition never share a window of play, so that any match falls in exactly one season.
