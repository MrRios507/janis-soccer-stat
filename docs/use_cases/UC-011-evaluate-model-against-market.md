# Use Case: Evaluate Model Against Market

## Overview

**Use Case ID:** UC-011  
**Use Case Name:** Evaluate Model Against Market  
**Primary Actor:** Modeler  
**Goal:** Score a recorded model and the betting market on the same played matches, so that it is known whether the model carries information the market does not already price in  
**Status:** Deferred

## Preconditions

- The model is recorded together with its training period
- The matches to be judged have been played and carry a result
- Closing odds are stored for those matches

## Main Success Scenario

1. Modeler asks for a recorded model to be judged over a period.
2. System confirms that the model is recorded and that the period begins after its training period ends.
3. System gathers the matches of the period that were played and carry a result.
4. System gathers the forecasts the model issued for those matches.
5. System gathers the closing odds of those matches.
6. System turns each set of closing odds into probabilities, taking out the operator's margin so that the three add up to one.
7. System scores the model and the market over the same matches, rewarding well judged probabilities rather than correct picks.
8. System presents both scores side by side, together with the matches where the two disagreed most.
9. Modeler judges whether the model adds anything to what the market already knew.

## Alternative Flows

### A1: Period Overlaps The Training Period

**Trigger:** The requested period begins before the model's training period ends (step 2)  
**Flow:**

1. System refuses to judge the model over that period.
2. System states that a model may not be judged on matches it learnt from.
3. Use case ends.

### A2: Model Issued No Forecast For Some Matches

**Trigger:** Some matches of the period carry no forecast from this model (step 4)  
**Flow:**

1. System leaves those matches out of the comparison.
2. System reports how many were left out.
3. Use case continues at step 5.

### A3: Matches Without Closing Odds

**Trigger:** Some matches carry no closing odds (step 5)  
**Flow:**

1. System leaves those matches out of the comparison so that both sides are scored on the same set.
2. System reports how many were left out.
3. Use case continues at step 6.

### A4: Too Few Matches To Judge

**Trigger:** Fewer matches remain than are needed for the comparison to mean anything (step 3)  
**Flow:**

1. System states that the comparison would not be meaningful and produces no score.
2. Use case ends.

## Postconditions

### Success Postconditions

- The model and the market carry a score computed over exactly the same matches
- The market probabilities used are free of the operator's margin and add up to one
- The matches of greatest disagreement are listed
- The stored model, forecasts and odds are unchanged

### Failure Postconditions

- No score is produced
- The stored model, forecasts and odds are unchanged
- The reason the comparison was refused is reported to the Modeler

## Business Rules

### BR-001: The Market Is The Benchmark

The closing price carries all the public information about a match. A model that does not approach it has learnt nothing useful, and without scoring the two together there is no way to know which is the case.

### BR-002: The Operator's Margin Comes Out First

Quoted prices always add up to more than one, because the operator's margin is built into them. Comparing against the raw prices would flatter the model by scoring it against a market deliberately shaded against the bettor.

### BR-003: Score The Probabilities, Not The Picks

The measure rewards probabilities that turn out to be well judged. Counting correct picks rewards always naming the favourite, which needs no model at all.

### BR-004: Both Sides Are Scored On The Same Matches

A match left out for one side is left out for both. Scoring the model on a different set from the market makes the comparison meaningless in a way that is very hard to notice afterwards.
