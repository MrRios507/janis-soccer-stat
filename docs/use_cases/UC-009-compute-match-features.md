# Use Case: Compute Match Features

## Overview

**Use Case ID:** UC-009  
**Use Case Name:** Compute Match Features  
**Primary Actor:** Modeler  
**Goal:** Produce the predictive variables of a match from information that existed before a stated cutoff, so that a model is never trained on anything that was unknowable at the time  
**Status:** Draft

## Preconditions

- The matches to compute features for are stored
- The named feature set version is defined

## Main Success Scenario

1. Modeler requests the features of a set of matches under a named feature set version.
2. System establishes the cutoff for each match, which is by default the moment that match starts.
3. System gathers, for each of the two teams, only the matches that started before that cutoff.
4. System gathers only the odds that were recorded before that cutoff.
5. System computes the variables that the named version defines.
6. System stores one set of variables per team per match, carrying the cutoff and the version that produced it.
7. System reports how many sets were computed and how many matches were refused.
8. Modeler confirms the variables are available for training.

## Alternative Flows

### A1: Cutoff Falls After The Match Starts

**Trigger:** The requested cutoff is later than the moment the match starts (step 2)  
**Flow:**

1. System refuses that match and stores nothing for it.
2. System states that a cutoff may never reach past the start of its own match.
3. Use case continues at step 7.

### A2: Too Little History Before The Cutoff

**Trigger:** A team has played fewer matches before the cutoff than the version requires (step 3)  
**Flow:**

1. System computes the variables it can and leaves the rest empty.
2. System marks the set as built on short history.
3. Use case continues at step 5.

### A3: Variables Already Computed

**Trigger:** A set already exists for that match, team, version and cutoff (step 6)  
**Flow:**

1. System leaves the existing set untouched.
2. Use case continues at step 7.

### A4: Feature Set Version Unknown

**Trigger:** The named version is not defined (step 5)  
**Flow:**

1. System refuses the whole request and stores nothing.
2. Use case ends.

## Postconditions

### Success Postconditions

- Every accepted match carries one set of variables per team, each naming its cutoff and its version
- No stored variable reflects a match that started after its cutoff or odds recorded after it
- Matches whose cutoff reached past their own start are refused and carry nothing
- Sets computed earlier under the same version and cutoff are unchanged

### Failure Postconditions

- No set of variables is stored
- Sets computed by earlier requests remain unchanged

## Business Rules

### BR-001: Nothing After The Cutoff May Be Read

Computing a set of variables may consider only matches that started before its cutoff and odds recorded before it. This is the single rule the whole project rests on: a variable that absorbs a later result produces a model that scores brilliantly in evaluation and fails in use, and nothing downstream would reveal the cause.

### BR-002: The Cutoff Travels With The Variables

Every stored set carries the cutoff it was built under. Without it there is no way to prove afterwards that the rule above was respected.

### BR-003: A Feature Set Version Is Never Edited In Place

Changing how a variable is computed creates a new version. Two models are comparable only when the meaning of their variables is fixed, and silently redefining a variable makes every earlier measurement a lie.

### BR-004: Short History Is Marked, Not Hidden

A team with little history before the cutoff yields an incomplete set, and it is marked as such. Quietly filling the gap with an average would present a guess as an observation.
