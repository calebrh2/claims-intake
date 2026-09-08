# Rubric

Scored out of 100.

## Test-first evidence (20 points)

| Level | Points | Descriptor |
| --- | ---: | --- |
| Excellent | 20 | The history shows failing tests committed before each corresponding implementation, in coherent increments. Tests were written from the contract and the work items, and nothing in them could have been derived from reading the implementation. No test was adjusted after the fact. |
| Proficient | 15 | The sequence holds and is visible, but the increments are coarse, so one commit carries most of the tests and another carries most of the implementation and the correspondence has to be inferred. |
| Developing | 9 | Tests precede implementation for some rules and not others, or a test was modified after the implementation was written without a contract line justifying it. |
| Inadequate | 3 | The history shows implementation and tests arriving together, so there is no evidence the specification preceded the solution, whatever the order actually was. |

## Rule engine correctness (25 points)

| Level | Points | Descriptor |
| --- | ---: | --- |
| Excellent | 25 | Every rule matches its contract row including boundary direction, code, and status. Evaluation order matches section 4.1. V-6 is placed deliberately, the placement preserves both the ordering and the separation between deciding and doing, and the reasoning is recorded where a reader will find it. |
| Proficient | 19 | All rules are correct and the order holds. The V-6 placement works but entangles the repository with the decision path more than necessary, or the reasoning is absent so the next reader has to reconstruct it. |
| Developing | 12 | One boundary is inverted, or one rule is missing from the ordered evaluation, or the order does not match the contract, so the caller can receive the wrong reason for a notification failing several rules. |
| Inadequate | 5 | Rules were implemented against a plausible reading rather than against the contract, and the discrepancies were not caught in review. |

## Dependency boundary (20 points)

| Level | Points | Descriptor |
| --- | ---: | --- |
| Excellent | 20 | The service layer converts PolicyNotFound into V-1 and lets PolicyLookupFailed propagate with its reason intact, tested across all three reasons. No handler catches more than it can answer for. A reader can see the distinction being preserved rather than having to trust it. |
| Proficient | 15 | The distinction holds and is tested, but one handler is broader than it needs to be, or only one or two of the three reasons are exercised. |
| Developing | 9 | The two conditions are distinguished in the code and the distinction is not tested, so nothing would catch a future change that collapses them. |
| Inadequate | 3 | A broad handler treats a lookup failure as an absent policy, which means the service will report that a policy does not exist when it does not know. |

## Pipeline (15 points)

| Level | Points | Descriptor |
| --- | ---: | --- |
| Excellent | 15 | All three checks run on pull requests, each can fail the job, dependencies install frozen, mypy covers tests as well as source, actions are pinned. The gate was verified by observing a real failure, and the observation is recorded including the case where protection is not configured. |
| Proficient | 11 | The workflow is correct and complete. Verification was performed but recorded as an assertion that it worked rather than as an observation of what happened. |
| Developing | 7 | The workflow runs the checks but one is scoped too narrowly to enforce much, or dependencies re-resolve, or actions are unpinned, so the gate does not check what it appears to check. |
| Inadequate | 2 | A step cannot fail the job, or the workflow does not run on pull requests, so nothing is gated regardless of what the file appears to say. |

## Agent decision log (20 points)

| Level | Points | Descriptor |
| --- | ---: | --- |
| Excellent | 20 | Both entries describe a real decision with a consequence. Each reason cites a contract section, an acceptance criterion, or a specific failure that would have occurred. The rejected change is genuinely something that would have passed review from someone reading less carefully. |
| Proficient | 15 | Both entries are substantive and referenced. One reason is sound but stated generally enough that it would apply to almost any change. |
| Developing | 9 | Entries describe what happened without establishing why the decision was correct, or one reason rests on preference rather than on the contract. |
| Inadequate | 3 | The log records that changes were reviewed and accepted, which is a description of the process rather than evidence of judgment. |
