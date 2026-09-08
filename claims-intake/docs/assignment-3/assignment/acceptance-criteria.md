Lab component produced
Component C3. Tomorrow's HTTP layer calls submit_notification and maps its outcomes to responses, and tomorrow's integration tests assert those responses end to end. The pipeline you write today is the gate the lab's pull request has to pass.

Interface contract fixed and consumed
Consumes C1 and C2. Rules, codes, boundaries, and evaluation order come from the contract. The objects come from models.py and are never bypassed.

Fixes C3. evaluate_notification(notification, policy) -> RuleFailure | None. submit_notification(notification, client, repository) -> ValidationOutcome, where ValidationOutcome carries whether the notification was accepted, the claim reference if it was, and the rule failure if it was not. The propagation rule that PolicyLookupFailed is not caught in the service layer. The three required checks in checks.yaml.

Acceptance criteria
Each criterion is met or not met. There is no partial credit within a criterion.

git log shows a commit containing the tests for a rule before any commit containing that rule's implementation.
Every rule V-1 through V-7 has at least one parametrized test case, with named ids.
Every comparison in the rule table has a case on each side of its boundary and a case on the boundary itself.
V-2 treats a loss on the inception date as covered and V-7 treats a loss on the cancellation date as not covered, and both are asserted by tests.
WI-0158 AC-3 is covered by a case where cancellation_date is absent.
WI-0151 AC-3 is covered by a case demonstrating that a rejected notification is not a duplicate.
No test in tests/unit/test_validation.py was modified after the implementation was written, and the history shows this.
evaluate_notification performs no I/O, writes nothing, and takes only a notification and a policy.
PolicyNotFound produces the V-1 failure with code POLICY_NOT_FOUND.
PolicyLookupFailed propagates out of submit_notification uncaught, with its reason intact, and a test demonstrates this for all three reasons.
No exception handler in service.py catches more broadly than the conditions it can answer for.
The order in which rules are evaluated matches section 4.1 of the contract, and V-6 is placed so that the order holds without a repository lookup inside POLICY_RULES.
checks.yaml triggers on pull requests, installs from the lockfile without re-resolving, runs all three tools with mypy covering source and tests, pins its actions, and contains no step that suppresses its own failure.
The observation from step 8 is recorded, stating whether a failing required check blocked the merge.
docs/agent-log.md contains two entries, each naming the change, the decision, and a reason referenced to a contract section, an acceptance criterion, or a specific failure.
ruff check and mypy both exit zero with no suppression added to achieve it, and the full suite passes.