# Use Case: Resolve Held Record

## Overview

**Use Case ID:** UC-014  
**Use Case Name:** Resolve Held Record  
**Primary Actor:** Data Engineer  
**Goal:** Decide, for every published team name that collection could not bind on its own, which known team it refers to, so that the records waiting on it can finally be stored  
**Status:** Draft

## Preconditions

- At least one held record is waiting to be resolved
- The collection that held it is no longer running

## Main Success Scenario

1. Data Engineer asks for the records waiting to be resolved.
2. System lists them grouped by publisher, each showing the published name and where it appeared.
3. Data Engineer selects a held record.
4. System shows the known candidates it weighed and how closely each one matched.
5. Data Engineer binds the published name to one of the known candidates.
6. System records the name as an alternative name of that team, so that later collections reuse it without asking again.
7. System releases the records that were waiting on that value and stores them.
8. System marks the held record as resolved, noting when.
9. System reports how many records were released.
10. Data Engineer confirms that the queue is clear.

## Alternative Flows

### A1: Nothing Waiting

**Trigger:** No held record is waiting (step 2)  
**Flow:**

1. System states that the queue is empty.
2. Use case ends.

### A2: The Name Belongs To A New Team

**Trigger:** No known candidate is the right one, and the name belongs to a genuinely new club (step 5)  
**Flow:**

1. Data Engineer registers the new team.
2. System binds the published name to the team just registered.
3. Use case continues at step 6.

### A3: The Name Is Not Worth Keeping

**Trigger:** Data Engineer judges that the name refers to a club outside the scope being collected (step 5)  
**Flow:**

1. Data Engineer marks the held record as discarded.
2. System leaves the waiting records unstored and stops offering the value for review.
3. Use case continues at step 9.

### A4: Released Records Still Cannot Be Stored

**Trigger:** A record released by the binding fails to store for another reason (step 7)  
**Flow:**

1. System holds that record again, carrying the new reason.
2. System stores the records that did succeed.
3. Use case continues at step 8.

## Postconditions

### Success Postconditions

- Each resolved name is bound to exactly one known team
- The name is recorded as an alternative name of that team, so later collections meeting it bind it without review
- The records that were waiting on the value are stored and attributed to the bound entity
- The held record carries the moment it was resolved and no longer appears in the queue

### Failure Postconditions

- The held record stays waiting and is offered again at the next review
- The records waiting on it stay unstored and are attributed to nothing
- No binding is recorded
- A record marked discarded stays visible as discarded, and what depended on it stays unstored

## Business Rules

### BR-001: Only A Person Resolves A Held Record

A record reaches this queue precisely because the system was not confident enough to decide. Letting it decide here anyway, with the same information, would defeat the purpose of holding it.

### BR-002: A Resolution Outlives The Record It Cleared

Resolving a name records it as an alternative name of the team, so every later occurrence is bound automatically. Otherwise the same name would return to the queue on every collection.

### BR-003: Discarding Is Not Deleting

A discarded record stays visible, marked as discarded, and what depended on it stays unstored. A value judged irrelevant today may turn out to matter, and silently erasing it would hide that data was ever dropped.

### BR-004: Only Team Names Are Held

In increment 1 the only value a collection can fail to bind is a team name, so that is the only kind this queue carries. Players and a publisher's own match references arrive with the increments that collect them, and each widens this queue rather than changing how it works.
