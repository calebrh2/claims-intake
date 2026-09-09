Day 3 Assignment: Build the Rule Engine Test-First and Gate It
Objective
Build the decision layer of the service, test-first, and put a pipeline in front of it that can refuse a change.

This is the day the three strands of the week meet. Your contract says what the rules are. Your models guarantee the objects the rules operate on. Today you write the tests from the contract before the implementation exists, delegate the implementation against those tests, review what comes back with the contract open, and then build the gate that will keep all of it true after you stop paying attention.

The order matters and the order is graded. A branch that arrives with everything green and no evidence of sequence has not done this assignment.

Prerequisites
Read all four Day 3 articles before starting.

Your Day 1 and Day 2 deliverables are complete and committed. In particular, section 4.1 of your contract states the full evaluation order and section 6 maps every code to a status.

Confirm the starter material. src/claims/policy_client.py ships complete. PolicyLookupFailed carries a reason attribute taking one of timeout, unreachable, or unparsable, which is what lets the HTTP layer choose between the three 5xx statuses tomorrow. StubPolicyClient can be configured to raise either exception, and to raise PolicyLookupFailed with any of the three reasons.

src/claims/service.py ships with evaluate_policy_exists written as the pattern the remaining rules follow. Everything else in it is a stub.

Instructions
1. Write the failing tests first. tests/unit/test_validation.py. One parametrized test per rule, covering every comparison on both sides of the boundary and on the boundary itself, plus every acceptance criterion on the work items including the ones about absence. Write them from docs/api-contract.md and docs/requirements-brief.md. Do not open service.py while you do this.

2. Watch each test fail for the right reason. A failure naming a function that does not exist tells you nothing about your assertion. Add stubs, run again, and confirm each test fails on its assertion with the values you expected.

3. Commit the failing tests. Before any implementation exists. This commit is the evidence that the specification preceded the solution, and there is no other way to produce it after the fact.

4. Decide where V-6 lives. The duplicate rule needs the repository, and the other rules are pure functions of a notification and a policy. Putting a repository lookup inside POLICY_RULES breaks the separation between deciding and doing that you have been building all week. Resolve this deliberately, keep the evaluation order your contract specifies, and record the decision in a comment where the next reader will find it.

5. Implement the rules. Delegate this against your failing tests, using a task statement that names the outcome, the authority, and the boundary. The tests are not to be modified. Then review what comes back with your contract open, in order of consequence rather than in diff order, and check for what is absent as well as what is present.

6. Implement the service layer. evaluate_notification takes a notification and a policy and returns RuleFailure | None. It has no side effects and touches nothing outside itself. submit_notification orchestrates: it resolves the policy through the client, evaluates, and records only if evaluation passed.

The dependency boundary is the part to get right. PolicyNotFound means the policy master answered and said no, which is V-1, and it becomes a RuleFailure like any other rule outcome. PolicyLookupFailed means you do not know, which is not a rule outcome at all, and it must reach the HTTP layer intact so tomorrow's routes can map its reason to the right status. Do not catch what you cannot answer.

7. Author the pipeline. .github/workflows/checks.yaml. It runs on pull requests. It installs from the lockfile without re-resolving. It runs ruff, mypy over both source and tests, and pytest. Every step can fail the job. Third party actions are pinned.

8. Confirm the gate is a gate. Open a pull request from your branch. Push a commit that deliberately fails one check. Observe whether the merge is blocked or merely marked. Record what you observed. If it is not blocked, that is a finding about the repository configuration and you report it rather than working around it.

9. Write the agent decision log. docs/agent-log.md. Pick two changes the agent produced during this assignment: one you accepted and one you rejected or corrected. For each, record what it produced, what you decided, and the reason, referenced to a contract section, a work item acceptance criterion, or a specific failure it would have caused. Reasons that amount to preference do not count. This is a record of engineering judgment and it is graded as one.

Out of scope today. api/routes.py, the Dockerfile, and integration tests are tomorrow. The pipeline builds nothing today.

Deliverable
Committed to your branch, in this order.

tests/unit/test_validation.py, committed failing.

src/claims/service.py with the rules, POLICY_RULES, evaluate_notification, and submit_notification.

.github/workflows/checks.yaml.

docs/agent-log.md.

Plus any contract amendment your work today required.