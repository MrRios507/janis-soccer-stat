# Use Case: Predict Scheduled Match

## Overview

**Use Case ID:** UC-012  
**Use Case Name:** Predict Scheduled Match  
**Primary Actor:** Analyst  
**Goal:** Obtain the probability of a home win, a draw and an away win for a match that has not been played, before it starts  
**Status:** Draft

## Preconditions

- The match is stored and has not yet started
- A recorded model exists whose feature set version can be computed for the match

## Main Success Scenario

1. Analyst asks for the forecast of a scheduled match, naming the model to use.
2. System confirms that the match is stored and has not yet started.
3. System sets the cutoff to the present moment.
4. System obtains the variables of both teams computed under that cutoff.
5. System applies the named model to those variables.
6. System records the resulting probabilities of home win, draw and away win, together with the model and the cutoff.
7. System presents the probabilities alongside the market's, where odds have been quoted.
8. Analyst reads the forecast before the match starts.

## Alternative Flows

### A1: Match Has Already Started

**Trigger:** The match started before the forecast was asked for (step 2)  
**Flow:**

1. System refuses to forecast the match and records nothing.
2. System states that a forecast may only be issued beforehand.
3. Use case ends.

### A2: Variables Not Yet Computed

**Trigger:** No variables exist for the match under the present cutoff (step 4)  
**Flow:**

1. System computes the variables for both teams under that cutoff.
2. Use case continues at step 5.

### A3: Forecast Already Issued For This Cutoff

**Trigger:** The model already issued a forecast under the same cutoff (step 6)  
**Flow:**

1. System keeps the recorded forecast rather than issuing a second one.
2. Use case continues at step 7.

### A4: No Odds Quoted Yet

**Trigger:** No operator has quoted the match (step 7)  
**Flow:**

1. System presents the model's probabilities without a market comparison.
2. Use case continues at step 8.

## Postconditions

### Success Postconditions

- The match carries a forecast of three probabilities adding up to one
- The forecast records the model that issued it and the cutoff it was built on
- The cutoff of the forecast is earlier than the start of the match
- Forecasts issued earlier for the same match remain recorded

### Failure Postconditions

- No forecast is recorded for the match
- Forecasts issued earlier remain unchanged

## Business Rules

### BR-001: A Forecast Is Issued Only Beforehand

A match that has started can no longer be forecast. Allowing it would let a result quietly reach the information the forecast was built on, which is the one mistake this project is designed to prevent.

### BR-002: Every Forecast Carries Its Model And Its Cutoff

Without both, a forecast cannot be reproduced and cannot be fairly judged afterwards.

### BR-003: The Three Probabilities Add Up To One

Home win, draw and away win cover every outcome of the match, so their probabilities always total one.

### BR-004: A Forecast Is Never Revised In Place

Asking again later produces a new forecast under a new cutoff, recorded alongside the earlier one. Keeping both shows how the view of a match moved as its kickoff approached.
