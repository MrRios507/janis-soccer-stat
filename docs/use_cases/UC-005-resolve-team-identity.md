# Use Case: Resolve Team Identity

## Overview

**Use Case ID:** UC-005  
**Use Case Name:** Resolve Team Identity  
**Primary Actor:** Data Engineer  
**Goal:** Bind every team name a publisher uses to the right known team, so that data gathered from different publishers accumulates on one team instead of splitting across several  
**Status:** Draft

## Preconditions

- A collection is under way that carries team names published by an external source
- The publisher is registered as a known source

## Main Success Scenario

1. Data Engineer starts a collection that carries published team names.
2. System takes the next published team name.
3. System looks for a binding already recorded between that publisher and that name.
4. System reduces the published name to a comparable form, setting aside capitalisation, accents and the usual club suffixes.
5. System compares the reduced name against the known teams and their alternative names.
6. System finds one candidate above the confidence threshold with no other candidate close behind it.
7. System binds the published name to that team and keeps the binding for later collections.
8. System records the published name as an alternative name of that team.
9. System repeats from step 2 until every published name has been handled.
10. Data Engineer confirms that the collection can proceed with every team resolved.

## Alternative Flows

### A1: Binding Already Recorded

**Trigger:** The publisher and name were bound in an earlier collection (step 3)  
**Flow:**

1. System reuses the recorded binding without comparing names again.
2. Use case continues at step 9.

### A2: No Confident Candidate

**Trigger:** No known team reaches the confidence threshold (step 6)  
**Flow:**

1. System holds the published name for manual review.
2. System leaves the records that depend on that name unstored.
3. System continues with the remaining names.
4. Use case continues at step 9.

### A3: Several Candidates Equally Close

**Trigger:** Two or more known teams score close to each other above the threshold (step 6)  
**Flow:**

1. System holds the published name for manual review rather than choosing between them.
2. System leaves the records that depend on that name unstored.
3. Use case continues at step 9.

### A4: Held Name Resolved By The Data Engineer

**Trigger:** Data Engineer reviews a name held by an earlier collection (step 2)  
**Flow:**

1. System shows the held name together with the candidates it considered.
2. Data Engineer either binds the name to an existing team or registers a new team for it.
3. System records the binding and releases the held records for collection.
4. Use case continues at step 9.

## Postconditions

### Success Postconditions

- Every published name met during the collection is bound to exactly one known team
- Each binding is recorded against its publisher and is reused by later collections without comparing names again
- Newly met names are recorded as alternative names of the team they were bound to

### Failure Postconditions

- Names that could not be resolved confidently are held for manual review, bound to no team
- The records that depend on a held name remain unstored and are not attributed to any team
- Bindings recorded earlier remain unchanged

## Business Rules

### BR-001: Below The Threshold The System Never Chooses

A published name is bound only when one candidate is clearly ahead of every other. Otherwise the name is held for a person to decide. A wrongly bound team silently corrupts the entire history of two clubs, and nothing downstream would reveal it.

### BR-002: A Binding Is Made Once And Then Trusted

Once a publisher's name is bound to a team, later collections reuse that binding directly. Names are never compared a second time, so a publisher renaming a club mid-season cannot quietly split its history.

### BR-003: Identifiers Decide, Names Only Introduce

Where a publisher gives a team its own stable identifier, the binding is keyed on that identifier. The name is used only to find the team the first time, because publishers change display names far more often than identifiers.

### BR-004: A Held Name Blocks Only Its Own Records

Holding a name never halts the collection. Everything that does not depend on the unresolved team is stored as usual, and the held records join later once a person resolves the binding.

### BR-005: Registering A New Team Is A Human Decision

The system never creates a team on its own. A name with no confident candidate may be a genuinely new club or a new spelling of an existing one, and only a person can tell the two apart.
