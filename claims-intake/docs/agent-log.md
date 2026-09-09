# Agent decision log

Day 3 record of engineering judgment. Reasons cite a contract section, a work-item
acceptance criterion, or a specific failure. Preference is not a reason.

## Accepted: V-7 exclusive, V-2 inclusive

**Change.** `evaluate_policy_not_cancelled` refuses a loss on the cancellation
date (`loss_date >= cancellation_date` → `POLICY_CANCELLED`).
`evaluate_loss_after_inception` accepts a loss on the inception date
(`loss_date < effective_date` is the only V-2 failure).

**Decision.** Keep both operators as written. Do not “align” cancellation with
inception.

**Reason.** Contract section 4.2 states `loss_date >= effective_date` for V-2 and
`loss_date < cancellation_date` for V-7, and the prose under the table says a
loss on the inception date is covered (WI-0142 AC-3) while a loss on the
cancellation date is not (WI-0158 AC-2). The same inclusive operator on both
dates would accept a loss on the cancellation date, which WI-0158 AC-2 forbids,
or would reject a loss on the inception date, which WI-0142 AC-3 forbids.

## Rejected: repository lookup inside POLICY_RULES / evaluate_notification

**Change.** The Day 2 stub had `evaluate_notification(notification, policy_client,
repository)` and would have made it natural to put V-6 (and V-1) in the same
ordered tuple as the pure policy comparisons.

**Decision.** Reject that shape. `evaluate_notification` takes only a
notification and a policy. `POLICY_RULES` is V-2, V-7, V-3, V-4, V-5.
`submit_notification` fetches the policy (V-1 / `PolicyNotFound`), calls
`evaluate_notification`, then `evaluate_not_duplicate` (V-6).

**Reason.** Assignment instructions step 4 and contract section 4.1: evaluation
order is V-1, V-2, V-7, V-3, V-4, V-5, V-6, and V-6 needs the repository.
Putting `find_matching` inside `POLICY_RULES` mixes deciding with doing. Giving
`evaluate_notification` a repository would also give it I/O, which the C3
interface forbids (`evaluate_notification(notification, policy) -> RuleFailure |
None`, no side effects). A reader who only checked that duplicates were detected
would have accepted the stub shape; it would still have violated the dependency
boundary and made `evaluate_notification` untestable without a store.

## Step 8: is the pipeline a gate?

Pull request: https://github.com/calebrh2/claims-intake/pull/3

A first `checks` run on the workflow commit succeeded
(https://github.com/calebrh2/claims-intake/actions/runs/34275940329). Commit
`208fb6e` then added `tests/unit/test_gate_probe.py` with `assert False`. The
next run failed at pytest
(https://github.com/calebrh2/claims-intake/actions/runs/34276006144): job `checks`
conclusion `FAILURE`, `test_deliberate_gate_failure` asserted false, process
exit code 1. ruff and mypy had already passed; the failing step failed the job.

GitHub still reported the pull request as **MERGEABLE** with
`mergeStateStatus: UNSTABLE`. There was no required-status-check protection:
the failing check was marked on the pull request and did not block merge.
That is a finding about repository configuration, not about the workflow file.
The probe commit was reverted after the observation so the branch is green
again.
