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

from claims.models import NotificationRequest, Policy, RuleFailure
from claims.policy_client import PolicyClient
from claims.repository import NotificationRepository


@dataclass(frozen=True)
class ValidationOutcome:
    """The result of submit_notification.

    `accepted` is what the caller branches on. When it is true, `claim_reference`
    is the reference issued for the new record. When it is false, `failure` is the
    rule that refused. A V-6 duplicate also carries the existing record's
    `claim_reference` so the HTTP layer can fill contract section 5.1.

    There is no status code here. Contract section 6 maps a code to a status, and
    that mapping is applied at the HTTP boundary.
    """

    accepted: bool
    claim_reference: str | None = None
    failure: RuleFailure | None = None


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
    return None


def evaluate_loss_after_inception(
    notification: NotificationRequest,
    policy: Policy,
) -> RuleFailure | None:
    """V-2. The loss must not precede policy inception.

    The boundary is stated in contract section 4.2 and in WI-0142 AC-3. A loss on
    the inception date is covered.
    """
    return None


def evaluate_policy_not_cancelled(
    notification: NotificationRequest,
    policy: Policy,
) -> RuleFailure | None:
    """V-7. Cover ends at the start of the cancellation date.

    Contract section 4.2 and WI-0158 AC-2: a loss on the cancellation date is not
    covered. WI-0158 AC-3: the rule is not applied when cancellation_date is null.
    """
    return None


def evaluate_loss_before_expiry(
    notification: NotificationRequest,
    policy: Policy,
) -> RuleFailure | None:
    """V-3. The loss must not fall after the policy expiry date."""
    return None


def evaluate_amount_within_limit(
    notification: NotificationRequest,
    policy: Policy,
) -> RuleFailure | None:
    """V-4. The estimated amount must not exceed the policy limit.

    An amount equal to the limit is within cover, per contract section 4.2.
    """
    return None


def evaluate_claim_type_covered(
    notification: NotificationRequest,
    policy: Policy,
) -> RuleFailure | None:
    """V-5. The claim type must be permitted on the policy's product."""
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
    return None


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
    return ValidationOutcome(accepted=False)
