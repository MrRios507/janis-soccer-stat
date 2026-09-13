# Use Case: Train Prediction Model

## Overview

**Use Case ID:** UC-010  
**Use Case Name:** Train Prediction Model  
**Primary Actor:** Modeler  
**Goal:** Fit a model over a bounded period of past matches and record it with everything needed to reproduce and compare it later  
**Status:** Draft

## Preconditions

- Variables have been computed for the matches in the intended training period
- The named feature set version is defined

## Main Success Scenario

1. Modeler requests training, stating a feature set version, a training period and an approach.
2. System confirms that the version is defined and that the period holds matches.
3. System gathers the sets of variables whose cutoff falls inside the training period.
4. System gathers the known results of those matches.
5. System fits the model to the gathered variables and results.
6. System measures the fitted model over a period that begins after the training period ends.
7. System records the model with its version, its approach, its training period, its measurements and where its fitted form is kept.
8. Modeler confirms that the model is recorded and comparable with the earlier ones.

## Alternative Flows

### A1: Training Period Holds Too Few Matches

**Trigger:** The period holds fewer matches than the approach requires (step 2)  
**Flow:**

1. System refuses the request and records no model.
2. System states how many matches the period holds.
3. Use case ends.

### A2: Variables Missing For Part Of The Period

**Trigger:** Some matches inside the period carry no computed variables (step 3)  
**Flow:**

1. System fits the model on the matches that do carry variables.
2. System records what share of the period was actually used.
3. Use case continues at step 4.

### A3: Measurement Period Overlaps The Training Period

**Trigger:** The stated measurement period begins before the training period ends (step 6)  
**Flow:**

1. System refuses to measure and records no model.
2. System states that a model may never be judged on matches it was fitted to.
3. Use case ends.

### A4: Model Name And Version Already Recorded

**Trigger:** A model with the same name and version is already recorded (step 7)  
**Flow:**

1. System refuses to replace the recorded model.
2. System asks for a new version.
3. Use case ends.

## Postconditions

### Success Postconditions

- The fitted model is recorded together with its feature set version, approach, training period and measurements
- The location of its fitted form is recorded, so the model can be used again without refitting
- The measurement covers only matches that start after the training period ends
- Models recorded earlier are unchanged

### Failure Postconditions

- No model is recorded
- Models recorded earlier are unchanged
- The reason the request was refused is reported to the Modeler

## Business Rules

### BR-001: A Model Is Judged Only On Its Future

Measurement covers matches that start after the training period ends, never matches the model was fitted to. Judging a model on its own training data reports how well it memorised, not how well it predicts.

### BR-002: A Recorded Model Is Never Overwritten

Each recorded model keeps its measurements for good. Replacing one in place would destroy the record of what was tried and make a claim of improvement impossible to check.

### BR-003: A Model Names The Variables It Learnt From

Every model records the feature set version it was fitted on. Comparing two models trained on differently defined variables is meaningless, and without the version nothing would show it.

### BR-004: Training Reads Stored Variables Only

Training uses the variables already computed and stored, never variables recomputed on the spot. The stored ones carry their cutoff and are therefore known to respect it.
