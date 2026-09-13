# Use Case: Reprocess Retained Documents

## Overview

**Use Case ID:** UC-006  
**Use Case Name:** Reprocess Retained Documents  
**Primary Actor:** Data Engineer  
**Goal:** Interpret documents already retained a second time, so that a correction to how a publisher is read can be applied to the whole history without asking that publisher for anything again  
**Status:** Draft

## Preconditions

- Documents obtained from the publisher are retained in their original form
- The way the publisher's documents are interpreted has been corrected
- The publisher and the seasons to be reprocessed are known

## Main Success Scenario

1. Data Engineer requests reprocessing for one publisher and a range of seasons.
2. System confirms that the publisher and the seasons are known.
3. System opens a collection run marked as a reprocessing run.
4. System gathers the documents retained for that publisher and those seasons.
5. System interprets the next retained document again, without asking the publisher for anything.
6. System records the results, updating what it already stored for that document.
7. System notes against the document that it was interpreted and when.
8. System repeats from step 5 until every gathered document has been interpreted.
9. System closes the run, reporting how many documents were interpreted, how many stored values changed and how many failed.
10. Data Engineer confirms that the corrected reading is in place across the history.

## Alternative Flows

### A1: Document Still Cannot Be Interpreted

**Trigger:** The corrected reading still fails on a document (step 5)  
**Flow:**

1. System records the reason against the document.
2. System leaves everything it had previously stored for that document unchanged.
3. Use case continues at step 8.

### A2: Nothing Retained For The Requested Range

**Trigger:** No document is retained for the publisher and seasons requested (step 4)  
**Flow:**

1. System closes the run as failed, stating that nothing was available to reprocess.
2. Use case ends.

### A3: Document Unchanged Since Its Last Interpretation

**Trigger:** The document and the way it is read are both unchanged since it was last interpreted (step 5)  
**Flow:**

1. System skips the document without interpreting it again.
2. Use case continues at step 8.

### A4: Reinterpretation Contradicts Stored Values

**Trigger:** The new reading produces different values from those already stored (step 6)  
**Flow:**

1. System replaces the stored values with the new ones.
2. System counts the change so that the closing report states how much the history moved.
3. Use case continues at step 7.

## Postconditions

### Success Postconditions

- Every retained document in the requested range has been interpreted with the corrected reading
- Stored data reflects the corrected reading across the whole range
- Each document carries the moment it was last interpreted
- The run is closed as successful, carrying the counts of documents interpreted, values changed and failures
- No request was made to the publisher

### Failure Postconditions

- Documents that still cannot be interpreted carry the reason, and the data previously stored for them is untouched
- The run is closed as failed, carrying the reason
- The retained documents themselves are unaltered

## Business Rules

### BR-001: Reprocessing Never Contacts The Publisher

This use case reads only what is already retained. That is the whole point: publishers rotate addresses and delete history, so the retained copy may be the only surviving one.

### BR-002: Retained Documents Are Never Altered

A retained document is written once and only ever read afterwards. If it could be edited, it would stop being evidence of what the publisher actually said.

### BR-003: A Failed Interpretation Leaves Earlier Data Standing

When a document cannot be read, whatever was stored from it before remains. A correction that breaks one document must not erase history that was previously right.

### BR-004: Reprocessing Is Repeatable

Running the reprocessing twice over the same range produces the same stored result. It may therefore be repeated freely while a correction is being refined.
