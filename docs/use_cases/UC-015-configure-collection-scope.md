# Use Case: Configure Collection Scope

## Overview

**Use Case ID:** UC-015  
**Use Case Name:** Configure Collection Scope  
**Primary Actor:** Data Engineer  
**Goal:** Declare which competitions and seasons the system collects and which sources feed them, so that every collection knows what it is expected to work on  
**Status:** Draft

## Preconditions

- The countries the competitions belong to are registered

## Main Success Scenario

1. Data Engineer states a competition the system should cover, with how it is contested, its territorial reach and its level.
2. System registers the competition.
3. Data Engineer states the seasons of that competition to be collected, each with its label and its window of play.
4. System registers the seasons and marks the one currently being played.
5. Data Engineer states a source the system should collect from, with the address it is reached at and the shortest delay it requires between requests.
6. System registers the source with its address and its required delay.
7. System confirms that the competition, its seasons and its sources are ready to be collected.
8. Data Engineer confirms that the scope is complete.

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

## Postconditions

### Success Postconditions

- The competition is registered, and each of its declared seasons carries its window of play
- Exactly one season of the competition is marked as currently being played
- Every source the system collects from is registered with its address and its required delay
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

### BR-004: Seasons Of One Competition Do Not Overlap

Two seasons of the same competition never share a window of play, so that any match falls in exactly one season.
