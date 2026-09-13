# Requirements

## Functional Requirements

| ID     | Title                          | User Story                                                                                                                                                              | Priority | Status |
|--------|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|--------|
| FR-001 | Historical Results Load        | As a data engineer, I want to load the published historical result and odds files so that the database has a starting point without depending on scraping.                  | High     | Open   |
| FR-002 | Shot Collection                | As a data engineer, I want to collect individual shots for each match so that expected goals are computed from the shot rather than taken pre-aggregated.                   | High     | Open   |
| FR-003 | Team Statistics Collection     | As a data engineer, I want to collect advanced team statistics so that the model has variables that do not derive from shots.                                               | Medium   | Open   |
| FR-004 | Lineup Collection              | As a data engineer, I want to collect lineups with minutes played so that historical squad availability can be derived.                                                     | Medium   | Open   |
| FR-005 | Collection Run Logging         | As an operator, I want every collection run recorded with its outcome so that it is possible to audit what was collected and when.                                          | High     | Open   |
| FR-006 | Raw Document Retention         | As a data engineer, I want to retain the original document of every download so that a parsing error can be corrected without returning to the source.                      | High     | Open   |
| FR-007 | Offline Reprocessing           | As a data engineer, I want to reparse retained documents without issuing requests so that fixing a parser does not consume source quota.                                    | High     | Open   |
| FR-008 | External Identifier Mapping    | As a data engineer, I want to record how each entity is identified in each source so that data from different sources consolidates onto the same entity.                    | High     | Open   |
| FR-009 | Normalized Alias Matching      | As a data engineer, I want to match new teams by normalized name similarity so that onboarding a source is not entirely manual.                                             | Medium   | Open   |
| FR-010 | Low Confidence Match Review    | As a data engineer, I want matches below the confidence threshold held for manual review so that a wrongly associated team does not contaminate the history.                | High     | Open   |
| FR-011 | Idempotent Collection          | As an operator, I want rerunning a collection to update existing records instead of duplicating them so that the process can be repeated safely.                            | High     | Open   |
| FR-012 | Scheduled Match Registration   | As an analyst, I want matches not yet played registered with their kickoff date and time so that they can receive predictions before they are played.                       | High     | Open   |
| FR-013 | Closing Odds Capture           | As a modeler, I want the closing odds of every match recorded so that a market reference exists to compare the model against.                                               | High     | Open   |
| FR-014 | Team History Query             | As an analyst, I want to query the matches of a team in chronological order alongside their statistics so that recent form is straightforward to compute.                   | High     | Open   |
| FR-015 | Feature Computation Cutoff     | As a modeler, I want match features computed using only information prior to a cutoff instant so that training does not absorb future information.                          | High     | Open   |
| FR-016 | Feature Set Versioning         | As a modeler, I want the feature set versioned so that models trained on different definitions can be compared.                                                             | Medium   | Open   |
| FR-017 | Training Window Boundaries     | As a modeler, I want to bound the window of matches used for training so that evaluation respects chronological order.                                                      | High     | Open   |
| FR-018 | Trained Model Registration     | As a modeler, I want every trained model recorded with its metrics and artifact location so that results are reproducible.                                                  | High     | Open   |
| FR-019 | Prediction Generation          | As an analyst, I want the home win, draw and away win probabilities of a scheduled match so that a forecast exists before kickoff.                                          | High     | Open   |
| FR-020 | Market Comparison              | As an analyst, I want to compare the model probability against the one implied by the closing odds so that it is visible where the model disagrees with the market.         | High     | Open   |
| FR-021 | Temporal Model Evaluation      | As a modeler, I want the model evaluated on matches after its training window so that the metric reflects real behaviour.                                                   | High     | Open   |
| FR-022 | Collection Resumption          | As an operator, I want to resume an interrupted collection from the last processed item so that a failure does not force repeating the whole batch.                        | Medium   | Open   |
| FR-023 | Data Coverage Report           | As an analyst, I want to see what percentage of matches has each statistic populated per league and season so that gaps are visible before modelling.                       | Medium   | Open   |
| FR-024 | Incomplete Match Detection     | As a data engineer, I want to identify played matches with no associated statistics so that they can be selectively recollected.                                            | Medium   | Open   |
| FR-025 | Historical Absence Derivation  | As a modeler, I want player unavailability periods derived from absence in lineups so that an absence signal exists without an injury feed.                                 | Low      | Open   |
| FR-026 | Collection Scope Declaration   | As a data engineer, I want to declare which competitions and seasons the system collects so that every collection knows what it is expected to work on.                     | High     | Open   |
| FR-027 | Source Registration            | As a data engineer, I want to register each source with the address it is reached at and the delay it requires between requests so that collection respects its limits.     | High     | Open   |
| FR-028 | Source Coverage Declaration    | As a data engineer, I want to record which statistics a source publishes for a competition so that data it never offers is not reported as a gap to be filled.              | Medium   | Open   |

## Non-Functional Requirements

| ID      | Title                        | Requirement                                                                                                          | Category        | Priority | Status |
|---------|------------------------------|----------------------------------------------------------------------------------------------------------------------|-----------------|----------|--------|
| NFR-001 | Team History Query Time      | Retrieving the last 10 matches of a team must complete in under 100 milliseconds.                                    | Performance     | High     | Open   |
| NFR-002 | Feature Generation Time      | Computing the features of a matchday of 10 matches must complete in under 30 seconds.                                | Performance     | Medium   | Open   |
| NFR-003 | Reprocessing Time            | Reparsing a full season from retained documents must complete in under 10 minutes with no network requests.          | Performance     | Medium   | Open   |
| NFR-004 | Supported Volume             | The system must sustain the defined query times with 200000 matches and 2000000 shots stored.                        | Scalability     | Medium   | Open   |
| NFR-005 | Transient Failure Retries    | Collection must retry up to 3 times with exponential backoff before marking an item as failed.                       | Availability    | High     | Open   |
| NFR-006 | Unattended Weekly Collection | The weekly collection must complete without manual intervention in at least 95 percent of weeks.                     | Availability    | Medium   | Open   |
| NFR-007 | Evaluation Reproducibility   | 2 evaluation runs with the same seed and the same cutoff instant must produce metrics differing by 0.                | Maintainability | High     | Open   |
| NFR-008 | Parser Test Coverage         | Document parsing modules must maintain test coverage of at least 80 percent.                                         | Maintainability | High     | Open   |
| NFR-009 | Source Isolation             | A format change in one source must be resolvable by modifying at most 1 parsing module.                              | Maintainability | Medium   | Open   |
| NFR-010 | No Secrets In Repository     | The repository must contain 0 credentials, verified by an automated scan on every commit.                            | Security        | High     | Open   |
| NFR-011 | Execution Portability        | The system must run without code changes on Linux and macOS with Python 3.11 or later.                               | Portability     | Low      | Open   |

## Constraints

| ID    | Title                      | Constraint                                                                                                          | Category    | Priority | Status |
|-------|----------------------------|---------------------------------------------------------------------------------------------------------------------|-------------|----------|--------|
| C-001 | Database Engine            | The system must use PostgreSQL 16 or later.                                                                         | Technical   | High     | Open   |
| C-002 | Implementation Language    | Collection and modelling must be implemented in Python 3.11 or later.                                               | Technical   | High     | Open   |
| C-003 | Data Source Cost           | Monthly data cost must be 0 dollars, with no paid interfaces contracted.                                            | Business    | High     | Open   |
| C-004 | Per Source Request Limits  | Collection must respect the minimum delay between requests declared by each source in its access policy.            | Technical   | High     | Open   |
| C-005 | Expected Goals Coverage    | Expected goals are available only from the 2014-15 season onward, the limit of the source that publishes them.      | Technical   | High     | Open   |
| C-006 | Competition Scope          | The system covers exclusively the five major European men's leagues.                                                | Business    | High     | Open   |
| C-007 | Use Of Collected Data      | Collected data is for personal use and must not be redistributed to third parties.                                  | Regulatory  | High     | Open   |
| C-008 | No Injury Data             | No free source exists for injuries or for lineups confirmed before kickoff.                                         | Technical   | Medium   | Open   |
| C-009 | Development Resources      | The project is developed by 1 person without full-time dedication.                                                  | Business    | Medium   | Open   |
| C-010 | Execution Infrastructure   | The system must run on a local machine, without depending on cloud services.                                        | Operational | Medium   | Open   |
| C-011 | Work Sequencing            | The historical load must be complete before the first model is trained.                                             | Schedule    | High     | Open   |
