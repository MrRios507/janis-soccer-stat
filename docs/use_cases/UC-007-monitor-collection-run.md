# Use Case: Monitor Collection Run

## Overview

**Use Case ID:** UC-007  
**Use Case Name:** Monitor Collection Run  
**Primary Actor:** Operator  
**Goal:** See what every collection run did and resume the ones that stopped early, so that a failure costs only the work that was left rather than the whole batch  
**Status:** Draft

## Preconditions

- At least one collection run has been opened
- No other run is in progress against the same publisher and target

## Main Success Scenario

1. Operator asks for the state of collection.
2. System lists the runs with their publisher, their target, when they started and ended, their outcome and their counts.
3. Operator selects a run that did not finish.
4. System shows the point at which that run stopped and the reason it stopped.
5. Operator asks for the run to be resumed.
6. System opens a new run that continues from the recorded point.
7. System processes the items that the earlier run never reached.
8. System closes the new run, reporting what it completed.
9. Operator confirms that the target is now fully collected.

## Alternative Flows

### A1: Every Run Finished

**Trigger:** No listed run stopped early (step 3)  
**Flow:**

1. System states that there is nothing to resume.
2. Use case ends.

### A2: Publisher Still Refusing Requests

**Trigger:** The publisher declines the first request of the resumed run (step 6)  
**Flow:**

1. System closes the new run immediately as partial, without advancing the recorded point.
2. System states that the publisher is still refusing and that the run may be resumed later.
3. Use case ends.

### A3: Operator Abandons The Run

**Trigger:** Operator decides the target is no longer wanted (step 5)  
**Flow:**

1. Operator marks the run as abandoned.
2. System stops offering it as resumable while keeping it visible in the list.
3. Use case ends.

### A4: Recorded Point No Longer Valid

**Trigger:** The publisher has reorganised its material so the recorded point cannot be found (step 6)  
**Flow:**

1. System reports that the run cannot be continued where it stopped.
2. System begins the target again from its start.
3. Use case continues at step 7.

## Postconditions

### Success Postconditions

- The target is fully collected, and the work already done by the earlier run was not repeated
- Both the interrupted run and the resuming run remain recorded with their own outcomes and counts
- The resuming run is closed as successful, carrying what it completed

### Failure Postconditions

- The interrupted run keeps its recorded stopping point and stays resumable
- No item is collected twice as a result of the attempt
- A run the Operator abandoned stays in the list, marked abandoned and no longer offered as resumable

## Business Rules

### BR-001: Every Run Is Recorded, Whatever Its Outcome

A run is recorded when it opens and closed with its outcome, including when it fails. A collection that left no trace cannot be audited, and the count of what was found against what was stored is what reveals a broken reading.

### BR-002: A Resumed Run Is A New Run

Resuming opens a new run rather than reopening the old one. The history of attempts stays intact, which is what makes a recurring failure against one publisher visible.

### BR-003: Resuming Never Skips Work

A resumed run starts exactly where the previous one stopped. Items already processed are not fetched again, and items never reached are never passed over.

### BR-004: Only One Run At A Time Per Target

Two runs never work the same publisher and target at once, so that the record of what was collected stays unambiguous and the publisher is never asked for more than it allows.
