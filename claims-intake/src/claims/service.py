"""Rule evaluation and notification submission.

This module owns the decision. It does not know it was reached over HTTP, which
is why it can be tested by calling a function with a typed object and asserting on
the result with no server running. It does not know where notifications are
stored either. It knows the rules.

Day 3 assignment. Build the remaining rules test-first against
`docs/api-contract.md` section 4.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from claims.models import ErrorCode, NotificationRequest, Policy, RuleFailure, RuleIdentifier
from claims.policy_client import PolicyClient, PolicyNotFound, PolicyRecord
from claims.repository import NotificationRepository


@dataclass(frozen=True)
class ValidationOutcome:
    """The result of submit_notification.

    `accepted` is what the caller branches on. When it is true, `claim_reference`
    is the reference issued for the new record. When it is false, `failure` is the
    rule that refused. A V-6 duplicate also carries the existing record's
    `claim_reference` so the HTTP layer can fill contract section 5.1.

    When a policy-backed rule refuses, `policy` is the record that rule compared
    against. The HTTP layer fills section 6 from this object. Looking the policy
    up again would not be the values the decision was made on, and a second
    lookup that failed would turn a 422 into a 5xx.

    There is no status code here. Contract section 6 maps a code to a status, and
    that mapping is applied at the HTTP boundary.
    """

    accepted: bool
    claim_reference: str | None = None
    failure: RuleFailure | None = None
    policy: Policy | None = None


def evaluate_policy_exists(
    notification: NotificationRequest,
    policy_client: PolicyClient,
) -> RuleFailure | None:
    """V-1. The policy must exist in the policy master.

    This rule is different from the others in one way that matters: it is the only
    one that reaches outside the service, so it is the only one that can fail for
    a reason that is not the caller's fault. `PolicyNotFound` is caught here and
    turned into an ordinary refusal, because a policy that does not exist is a
    fact about the caller's data. `PolicyLookupFailed` is deliberately not caught,
    because the caller did nothing wrong and the HTTP layer has to be able to tell
    the two apart. Contract section 6 fixes what each becomes.

    V-1 short circuits. Every other rule compares against a field on a policy, and
    if there is no policy there is nothing to compare against. Reporting
    LOSS_BEFORE_INCEPTION for a policy number that does not exist is not merely
    unhelpful, it is a false statement about the client's data (WI-0142, AC-4).
    """
    try:
        policy_client.get_policy(notification.policy_number)
    except PolicyNotFound:
        return RuleFailure(
            rule=RuleIdentifier("V-1"),
            code=ErrorCode("POLICY_NOT_FOUND"),
        )
    return None


def evaluate_loss_after_inception(
    notification: NotificationRequest,
    policy: Policy,
) -> RuleFailure | None:
    """V-2. The loss must not precede policy inception.

    The boundary is stated in contract section 4.2 and in WI-0142 AC-3. A loss on
    the inception date is covered.
    """
    if notification.loss_date < policy.effective_date:
        return RuleFailure(
            rule=RuleIdentifier("V-2"),
            code=ErrorCode("LOSS_BEFORE_INCEPTION"),
        )
    return None


def evaluate_policy_not_cancelled(
    notification: NotificationRequest,
    policy: Policy,
) -> RuleFailure | None:
    """V-7. Cover ends at the start of the cancellation date.

    Contract section 4.2 and WI-0158 AC-2: a loss on the cancellation date is not
    covered. WI-0158 AC-3: the rule is not applied when cancellation_date is null.
    """
    if policy.cancellation_date is None:
        return None
    if notification.loss_date >= policy.cancellation_date:
        return RuleFailure(
            rule=RuleIdentifier("V-7"),
            code=ErrorCode("POLICY_CANCELLED"),
        )
    return None


def evaluate_loss_before_expiry(
    notification: NotificationRequest,
    policy: Policy,
) -> RuleFailure | None:
    """V-3. The loss must not fall after the policy expiry date."""
    if notification.loss_date > policy.expiry_date:
        return RuleFailure(
            rule=RuleIdentifier("V-3"),
            code=ErrorCode("LOSS_AFTER_EXPIRY"),
        )
    return None


def evaluate_amount_within_limit(
    notification: NotificationRequest,
    policy: Policy,
) -> RuleFailure | None:
    """V-4. The estimated amount must not exceed the policy limit.

    An amount equal to the limit is within cover, per contract section 4.2.
    """
    if notification.estimated_amount > policy.limit:
        return RuleFailure(
            rule=RuleIdentifier("V-4"),
            code=ErrorCode("AMOUNT_EXCEEDS_LIMIT"),
        )
    return None


def evaluate_claim_type_covered(
    notification: NotificationRequest,
    policy: Policy,
) -> RuleFailure | None:
    """V-5. The claim type must be permitted on the policy's product."""
    if notification.claim_type not in policy.permitted_claim_types:
        return RuleFailure(
            rule=RuleIdentifier("V-5"),
            code=ErrorCode("TYPE_NOT_COVERED"),
        )
    return None


def evaluate_not_duplicate(
    notification: NotificationRequest,
    repository: NotificationRepository,
) -> RuleFailure | None:
    """V-6. A recorded notification with the same loss event is a duplicate.

    WI-0151 AC-3: a rejected notification was never recorded, so it is not a
    duplicate. This function is not a member of POLICY_RULES; see the comment
    on that tuple.
    """
    existing = repository.find_matching(
        notification.policy_number,
        notification.loss_date,
        notification.claim_type,
    )
    if existing is not None:
        return RuleFailure(
            rule=RuleIdentifier("V-6"),
            code=ErrorCode("DUPLICATE_NOTIFICATION"),
        )
    return None


# V-6 is not in this tuple. Duplicate detection needs the repository, and putting
# a lookup inside POLICY_RULES would mix deciding with doing. V-1 runs at fetch
# in submit_notification; V-6 runs after these pure rules so section 4.1 order
# holds: V-1, V-2, V-7, V-3, V-4, V-5, V-6.
PolicyRule = Callable[[NotificationRequest, Policy], RuleFailure | None]
POLICY_RULES: tuple[PolicyRule, ...] = (
    evaluate_loss_after_inception,
    evaluate_policy_not_cancelled,
    evaluate_loss_before_expiry,
    evaluate_amount_within_limit,
    evaluate_claim_type_covered,
)


def evaluate_notification(
    notification: NotificationRequest,
    policy: Policy,
) -> RuleFailure | None:
    """Evaluate the pure policy rules and return the first failure, if any.

    A notification can violate several rules at once and the caller sees one
    reason, so the order this function evaluates in is a caller-visible behavior.
    It is fixed by contract section 4.1 and by nothing else. If you find yourself
    choosing an order here, the contract is incomplete and the fix belongs there.

    Takes only a notification and a policy. No I/O, no repository, no client.
    """
    for rule in POLICY_RULES:
        failure = rule(notification, policy)
        if failure is not None:
            return failure
    return None


def _policy_from_record(record: PolicyRecord) -> Policy:
    """Lift the master's record into the service Policy the rules compare."""
    return Policy(
        policy_number=record.policy_number,
        product=record.product,
        effective_date=record.effective_date,
        expiry_date=record.expiry_date,
        cancellation_date=record.cancellation_date,
        limit=record.limit,
        permitted_claim_types=record.permitted_claim_types,
    )


def submit_notification(
    notification: NotificationRequest,
    policy_client: PolicyClient,
    repository: NotificationRepository,
) -> ValidationOutcome:
    """Validate, and record only if every rule passed.

    Nothing is written before the decision is made. A notification is either
    recorded with a claim reference or it does not exist, and there is no state in
    between for a later reader to interpret.
    """
    try:
        record = policy_client.get_policy(notification.policy_number)
    except PolicyNotFound:
        return ValidationOutcome(
            accepted=False,
            failure=RuleFailure(
                rule=RuleIdentifier("V-1"),
                code=ErrorCode("POLICY_NOT_FOUND"),
            ),
        )

    policy = _policy_from_record(record)
    failure = evaluate_notification(notification, policy)
    if failure is not None:
        return ValidationOutcome(accepted=False, failure=failure, policy=policy)

    duplicate = evaluate_not_duplicate(notification, repository)
    if duplicate is not None:
        existing = repository.find_matching(
            notification.policy_number,
            notification.loss_date,
            notification.claim_type,
        )
        return ValidationOutcome(
            accepted=False,
            claim_reference=None if existing is None else existing.claim_reference,
            failure=duplicate,
        )

    recorded = repository.record(notification, accepted=True)
    return ValidationOutcome(
        accepted=True,
        claim_reference=None if recorded is None else recorded.claim_reference,
    )
