# Use Case: Resolve Held Record

## Overview

**Use Case ID:** UC-014  
**Use Case Name:** Resolve Held Record  
**Primary Actor:** Data Engineer  
**Goal:** Decide, for every published value that collection could not bind on its own, which known team, match or player it refers to, so that the records waiting on it can finally be stored  
**Status:** Draft

## Preconditions

- At least one held record is waiting to be resolved
- The collection that held it is no longer running

## Main Success Scenario

1. Data Engineer asks for the records waiting to be resolved.
2. System lists them grouped by kind and by publisher, each showing the published value and where it appeared.
3. Data Engineer selects a held record.
4. System shows the known candidates it weighed and how closely each one matched.
5. Data Engineer binds the published value to one of the known candidates.
6. System records the binding against the publisher, so that later collections reuse it without asking again.
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

### A2: The Value Names Something New

**Trigger:** No known candidate is the right one, and the value names a genuinely new team or player (step 5)  
**Flow:**

1. Data Engineer registers the new team or player.
2. System binds the published value to what was just registered.
3. Use case continues at step 6.

### A3: The Value Is Not Worth Keeping

**Trigger:** Data Engineer judges that the value refers to something outside the scope being collected (step 5)  
**Flow:**

1. Data Engineer marks the held record as discarded.
2. System leaves the waiting records unstored and stops offering the value for review.
3. Use case continues at step 9.

### A4: A Held Match Has No Counterpart

**Trigger:** The held value names a match, and no stored match corresponds to it (step 5)  
**Flow:**

1. System refuses to create a match from the review.
2. Data Engineer leaves the record waiting until the historical load supplies the match.
3. Use case continues at step 9.

### A5: Released Records Still Cannot Be Stored

**Trigger:** A record released by the binding fails to store for another reason (step 7)  
**Flow:**

1. System holds that record again, carrying the new reason.
2. System stores the records that did succeed.
3. Use case continues at step 8.

## Postconditions

### Success Postconditions

- Each resolved value is bound to exactly one known team, match or player
- The binding is recorded against its publisher, so later collections meeting the same value bind it without review
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

### BR-002: A Resolution Binds The Publisher, Not Just The Record

Resolving a value records a binding for that publisher, so every later occurrence is bound automatically. Otherwise the same name would return to the queue on every collection.

### BR-003: Discarding Is Not Deleting

A discarded record stays visible, marked as discarded, and what depended on it stays unstored. A value judged irrelevant today may turn out to matter, and silently erasing it would hide that data was ever dropped.

### BR-004: Resolution Never Creates A Match

A new team or player may be registered here, but a match may not. Matches carry a result and odds that only the historical load provides, so a match created from a review would be permanently incomplete. See UC-002 BR-003.
