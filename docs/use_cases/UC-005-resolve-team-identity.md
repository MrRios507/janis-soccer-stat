# Use Case: Resolve Team Identity

## Overview

**Use Case ID:** UC-005  
**Use Case Name:** Resolve Team Identity  
**Primary Actor:** Data Engineer  
**Goal:** Bind every team name a publisher uses to the right known team, so that everything published about a club accumulates on one team instead of splitting across several  
**Status:** Draft

## Preconditions

- A collection is under way that carries team names published by an external source
- The publisher is registered as a known source

## Main Success Scenario

1. Data Engineer starts a collection that carries published team names.
2. System takes the next published team name.
3. System looks for a known team already recorded under that name.
4. System reduces the published name to a comparable form, setting aside capitalisation, accents and the usual club suffixes.
5. System compares the reduced name against the known teams and their alternative names.
6. System finds one candidate above the confidence threshold with no other candidate close behind it.
7. System records the published name as an alternative name of that team, so that later collections resolve it without comparing names again.
8. System repeats from step 2 until every published name has been handled.
9. Data Engineer confirms that the collection can proceed with every team resolved.

## Alternative Flows

### A1: Name Already Known

**Trigger:** The name is already recorded as an alternative name of a known team (step 3)  
**Flow:**

1. System reuses that team without comparing names again.
2. Use case continues at step 8.

### A2: No Confident Candidate

**Trigger:** No known team reaches the confidence threshold (step 6)  
**Flow:**

1. System holds the published name for manual review.
2. System leaves the records that depend on that name unstored.
3. System continues with the remaining names.
4. Use case continues at step 8.

### A3: Several Candidates Equally Close

**Trigger:** Two or more known teams score close to each other above the threshold (step 6)  
**Flow:**

1. System holds the published name for manual review rather than choosing between them.
2. System leaves the records that depend on that name unstored.
3. Use case continues at step 8.

### A4: Name Already Resolved By A Review

**Trigger:** The name was held by an earlier collection and a person has since resolved it (step 3)  
**Flow:**

1. System finds the alternative name recorded when the held record was resolved.
2. System reuses the team it points to without comparing names again.
3. Use case continues at step 8.

## Postconditions

### Success Postconditions

- Every published name met during the collection is bound to exactly one known team
- Every name met is recorded as an alternative name of the team it was bound to, and is reused by later collections without comparing names again

### Failure Postconditions

- Names that could not be resolved confidently are held for manual review, bound to no team
- The records that depend on a held name remain unstored and are not attributed to any team
- Alternative names recorded earlier remain unchanged

## Business Rules

### BR-001: Below The Threshold The System Never Chooses

A published name is bound only when one candidate is clearly ahead of every other. Otherwise the name is held for a person to decide. A wrongly bound team silently corrupts the entire history of two clubs, and nothing downstream would reveal it.

### BR-002: A Binding Is Made Once And Then Trusted

Once a published name is bound to a team, later collections reuse that binding directly. Names are never compared a second time, so a publisher renaming a club mid-season cannot quietly split its history.

### BR-003: A Held Name Blocks Only Its Own Records

Holding a name never halts the collection. Everything that does not depend on the unresolved team is stored as usual, and the held records join later once a person resolves the binding.

### BR-004: Registering A New Team Is A Human Decision

The system never creates a team on its own. A name with no confident candidate may be a genuinely new club or a new spelling of an existing one, and only a person can tell the two apart. That decision is taken while clearing the review queue, described in UC-014.
