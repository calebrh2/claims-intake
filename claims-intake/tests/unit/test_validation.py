"""Rule-boundary tests for Day 3 validation.

Written against `docs/api-contract.md` section 4 and the work-item acceptance
criteria in `docs/requirements-brief.md`. Each parametrized case names a
comparison on one side of a boundary, on the boundary, or an absence criterion.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from decimal import Decimal

import pytest

from claims.models import ClaimType, NotificationRequest, Policy, RuleFailure
from claims.policy_client import LookupFailureReason, PolicyLookupFailed, StubPolicyClient
from claims.repository import NotificationRepository
from claims.service import (
    evaluate_amount_within_limit,
    evaluate_claim_type_covered,
    evaluate_loss_after_inception,
    evaluate_loss_before_expiry,
    evaluate_not_duplicate,
    evaluate_notification,
    evaluate_policy_exists,
    evaluate_policy_not_cancelled,
    submit_notification,
)


def _code(failure: RuleFailure | None) -> str | None:
    return failure.code if failure else None


@pytest.mark.parametrize(
    ("loss_date", "expected"),
    [
        (date(2026, 2, 28), "LOSS_BEFORE_INCEPTION"),
        (date(2026, 3, 1), None),
        (date(2026, 3, 2), None),
    ],
    ids=[
        "day_before_inception_is_not_covered",
        "inception_date_itself_is_covered",
        "day_after_inception_is_covered",
    ],
)
def test_v2_cover_attaches_on_the_inception_date(
    make_notification: Callable[..., NotificationRequest],
    make_policy: Callable[..., Policy],
    loss_date: date,
    expected: str | None,
) -> None:
    """WI-0142 AC-1, AC-3. Contract §4.2 V-2: loss_date >= effective_date."""
    policy = make_policy(
        effective_date=date(2026, 3, 1),
        expiry_date=date(2026, 12, 31),
        cancellation_date=None,
    )
    notification = make_notification(loss_date=loss_date)

    failure = evaluate_loss_after_inception(notification, policy)

    assert _code(failure) == expected
    if expected is not None:
        assert failure is not None
        assert failure.rule == "V-2"


@pytest.mark.parametrize(
    ("cancellation_date", "loss_date", "expected"),
    [
        (date(2026, 6, 1), date(2026, 5, 31), None),
        (date(2026, 6, 1), date(2026, 6, 1), "POLICY_CANCELLED"),
        (date(2026, 6, 1), date(2026, 6, 2), "POLICY_CANCELLED"),
        (None, date(2026, 6, 1), None),
    ],
    ids=[
        "day_before_cancellation_is_covered",
        "cancellation_date_itself_is_not_covered",
        "after_cancellation_is_not_covered",
        "uncancelled_policy_is_unaffected",
    ],
)
def test_v7_ends_cover_at_the_cancellation_date(
    make_notification: Callable[..., NotificationRequest],
    make_policy: Callable[..., Policy],
    cancellation_date: date | None,
    loss_date: date,
    expected: str | None,
) -> None:
    """WI-0158 AC-1, AC-2, AC-3. Contract §4.2 V-7: loss_date < cancellation_date."""
    policy = make_policy(
        effective_date=date(2026, 3, 1),
        expiry_date=date(2026, 12, 31),
        cancellation_date=cancellation_date,
    )
    notification = make_notification(loss_date=loss_date)

    failure = evaluate_policy_not_cancelled(notification, policy)

    assert _code(failure) == expected
    if expected is not None:
        assert failure is not None
        assert failure.rule == "V-7"


@pytest.mark.parametrize(
    ("loss_date", "expected"),
    [
        (date(2026, 12, 30), None),
        (date(2026, 12, 31), None),
        (date(2027, 1, 1), "LOSS_AFTER_EXPIRY"),
    ],
    ids=[
        "day_before_expiry_is_covered",
        "expiry_date_itself_is_covered",
        "day_after_expiry_is_not_covered",
    ],
)
def test_v3_cover_includes_the_expiry_date(
    make_notification: Callable[..., NotificationRequest],
    make_policy: Callable[..., Policy],
    loss_date: date,
    expected: str | None,
) -> None:
    """Contract §4.2 V-3: loss_date <= expiry_date."""
    policy = make_policy(
        effective_date=date(2026, 3, 1),
        expiry_date=date(2026, 12, 31),
        cancellation_date=None,
    )
    notification = make_notification(loss_date=loss_date)

    failure = evaluate_loss_before_expiry(notification, policy)

    assert _code(failure) == expected
    if expected is not None:
        assert failure is not None
        assert failure.rule == "V-3"


@pytest.mark.parametrize(
    ("estimated_amount", "expected"),
    [
        (Decimal("9999.99"), None),
        (Decimal("10000.00"), None),
        (Decimal("10000.01"), "AMOUNT_EXCEEDS_LIMIT"),
    ],
    ids=[
        "amount_below_limit_is_within_cover",
        "amount_equal_to_limit_is_within_cover",
        "amount_above_limit_is_not_covered",
    ],
)
def test_v4_cover_includes_an_amount_equal_to_the_limit(
    make_notification: Callable[..., NotificationRequest],
    make_policy: Callable[..., Policy],
    estimated_amount: Decimal,
    expected: str | None,
) -> None:
    """Contract §4.2 V-4: estimated_amount <= limit."""
    policy = make_policy(
        effective_date=date(2026, 3, 1),
        expiry_date=date(2026, 12, 31),
        cancellation_date=None,
        limit=Decimal("10000.00"),
    )
    notification = make_notification(estimated_amount=estimated_amount)

    failure = evaluate_amount_within_limit(notification, policy)

    assert _code(failure) == expected
    if expected is not None:
        assert failure is not None
        assert failure.rule == "V-4"


@pytest.mark.parametrize(
    ("claim_type", "permitted_claim_types", "expected"),
    [
        ("collision", ("collision", "glass"), None),
        ("theft", ("collision", "glass"), "TYPE_NOT_COVERED"),
    ],
    ids=[
        "type_on_the_product_is_covered",
        "vocabulary_type_omitted_from_the_product_is_not_covered",
    ],
)
def test_v5_cover_is_the_product_permitted_set(
    make_notification: Callable[..., NotificationRequest],
    make_policy: Callable[..., Policy],
    claim_type: ClaimType,
    permitted_claim_types: tuple[ClaimType, ...],
    expected: str | None,
) -> None:
    """Contract §4.2 V-5: claim_type must be permitted on the policy's product."""
    policy = make_policy(
        effective_date=date(2026, 3, 1),
        expiry_date=date(2026, 12, 31),
        cancellation_date=None,
        permitted_claim_types=permitted_claim_types,
    )
    notification = make_notification(claim_type=claim_type)

    failure = evaluate_claim_type_covered(notification, policy)

    assert _code(failure) == expected
    if expected is not None:
        assert failure is not None
        assert failure.rule == "V-5"


@pytest.mark.parametrize(
    ("policy_number", "expected"),
    [
        ("NO-SUCH-POLICY", "POLICY_NOT_FOUND"),
        ("mot-4471", "POLICY_NOT_FOUND"),
        ("MOT-4471", None),
    ],
    ids=[
        "unknown_number_is_not_found",
        "differing_case_is_not_a_match",
        "existing_policy_is_not_v1",
    ],
)
def test_v1_policy_number_is_exact_string_equality(
    make_notification: Callable[..., NotificationRequest],
    policy_client: StubPolicyClient,
    policy_number: str,
    expected: str | None,
) -> None:
    """WI-0142 AC-4. Contract §4.2 V-1: exact match with the policy master."""
    notification = make_notification(policy_number=policy_number)

    failure = evaluate_policy_exists(notification, policy_client)

    assert _code(failure) == expected
    if expected is not None:
        assert failure is not None
        assert failure.rule == "V-1"


def test_v1_does_not_treat_lookup_failure_as_not_found(
    make_notification: Callable[..., NotificationRequest],
) -> None:
    """PolicyLookupFailed is not a V-1 outcome. The service cannot answer."""
    client = StubPolicyClient(fail_with="timeout")
    notification = make_notification(policy_number="MOT-4471")

    with pytest.raises(PolicyLookupFailed) as raised:
        evaluate_policy_exists(notification, client)

    assert raised.value.reason == "timeout"


def test_v6_three_field_match_is_a_duplicate(
    make_notification: Callable[..., NotificationRequest],
    repository: NotificationRepository,
) -> None:
    """WI-0151 AC-1. Contract §4.2 V-6: policy_number, loss_date, and claim_type."""
    recorded = make_notification()
    repository.record(recorded, accepted=True, recorded_on=date(2026, 4, 2))
    retry = make_notification()

    failure = evaluate_not_duplicate(retry, repository)

    assert _code(failure) == "DUPLICATE_NOTIFICATION"
    assert failure is not None
    assert failure.rule == "V-6"


@pytest.mark.parametrize(
    "override",
    [
        {"policy_number": "MOT-4472"},
        {"loss_date": date(2026, 4, 3)},
        {"claim_type": "theft"},
    ],
    ids=[
        "differing_policy_number_is_not_a_duplicate",
        "differing_loss_date_is_not_a_duplicate",
        "differing_claim_type_is_not_a_duplicate",
    ],
)
def test_v6_two_of_three_fields_is_not_a_duplicate(
    make_notification: Callable[..., NotificationRequest],
    repository: NotificationRepository,
    override: dict[str, object],
) -> None:
    """WI-0151 AC-1. Two of the three fields is not a match."""
    recorded = make_notification()
    repository.record(recorded, accepted=True, recorded_on=date(2026, 4, 2))
    retry = make_notification(**override)

    failure = evaluate_not_duplicate(retry, repository)

    assert failure is None


def test_v6_rejected_notification_is_not_a_duplicate(
    make_notification: Callable[..., NotificationRequest],
    repository: NotificationRepository,
) -> None:
    """WI-0151 AC-3. A rejected notification was never recorded."""
    rejected = make_notification()
    repository.record(rejected, accepted=False, recorded_on=date(2026, 4, 2))
    retry = make_notification()

    failure = evaluate_not_duplicate(retry, repository)

    assert failure is None


def test_evaluate_notification_reports_cancellation_before_expiry(
    make_notification: Callable[..., NotificationRequest],
    make_policy: Callable[..., Policy],
) -> None:
    """WI-0158 AC-4. Contract §4.1: V-7 before V-3 when both fail."""
    policy = make_policy(
        effective_date=date(2026, 3, 1),
        expiry_date=date(2026, 12, 31),
        cancellation_date=date(2026, 6, 1),
    )
    notification = make_notification(loss_date=date(2027, 1, 1))

    failure = evaluate_notification(notification, policy)

    assert _code(failure) == "POLICY_CANCELLED"
    assert failure is not None
    assert failure.rule == "V-7"


def test_evaluate_notification_reports_inception_before_cancellation(
    make_notification: Callable[..., NotificationRequest],
    make_policy: Callable[..., Policy],
) -> None:
    """Contract §4.1: V-2 before V-7 when both fail."""
    policy = make_policy(
        effective_date=date(2026, 3, 1),
        expiry_date=date(2026, 12, 31),
        cancellation_date=date(2026, 6, 1),
    )
    notification = make_notification(loss_date=date(2026, 2, 1))

    failure = evaluate_notification(notification, policy)

    assert _code(failure) == "LOSS_BEFORE_INCEPTION"
    assert failure is not None
    assert failure.rule == "V-2"


def test_evaluate_notification_passes_when_every_pure_rule_passes(
    make_notification: Callable[..., NotificationRequest],
    make_policy: Callable[..., Policy],
) -> None:
    policy = make_policy(
        effective_date=date(2026, 3, 1),
        expiry_date=date(2026, 12, 31),
        cancellation_date=None,
    )
    notification = make_notification(loss_date=date(2026, 4, 2))

    assert evaluate_notification(notification, policy) is None


def test_submit_unknown_policy_is_not_found_not_inception(
    make_notification: Callable[..., NotificationRequest],
    policy_client: StubPolicyClient,
    repository: NotificationRepository,
) -> None:
    """WI-0142 AC-4. An unknown number is V-1, not LOSS_BEFORE_INCEPTION."""
    notification = make_notification(
        policy_number="NO-SUCH-POLICY",
        loss_date=date(2020, 1, 1),
    )

    outcome = submit_notification(notification, policy_client, repository)

    assert outcome.accepted is False
    assert outcome.failure is not None
    assert outcome.failure.rule == "V-1"
    assert outcome.failure.code == "POLICY_NOT_FOUND"
    assert outcome.claim_reference is None
    assert (
        repository.find_matching(
            notification.policy_number,
            notification.loss_date,
            notification.claim_type,
        )
        is None
    )


@pytest.mark.parametrize(
    "reason",
    ["timeout", "unreachable", "unparsable"],
    ids=["timeout", "unreachable", "unparsable"],
)
def test_submit_propagates_policy_lookup_failed(
    make_notification: Callable[..., NotificationRequest],
    repository: NotificationRepository,
    reason: LookupFailureReason,
) -> None:
    """PolicyLookupFailed is not a rule outcome. All three reasons stay intact."""
    client = StubPolicyClient(fail_with=reason)
    notification = make_notification()

    with pytest.raises(PolicyLookupFailed) as raised:
        submit_notification(notification, client, repository)

    assert raised.value.reason == reason
    assert (
        repository.find_matching(
            notification.policy_number,
            notification.loss_date,
            notification.claim_type,
        )
        is None
    )


def test_submit_records_only_when_every_rule_passes(
    make_notification: Callable[..., NotificationRequest],
    policy_client: StubPolicyClient,
    repository: NotificationRepository,
) -> None:
    notification = make_notification()

    outcome = submit_notification(notification, policy_client, repository)

    assert outcome.accepted is True
    assert outcome.failure is None
    assert outcome.claim_reference is not None
    found = repository.find_matching(
        notification.policy_number,
        notification.loss_date,
        notification.claim_type,
    )
    assert found is not None
    assert found.claim_reference == outcome.claim_reference


def test_submit_duplicate_carries_the_existing_claim_reference(
    make_notification: Callable[..., NotificationRequest],
    policy_client: StubPolicyClient,
    repository: NotificationRepository,
) -> None:
    """WI-0151 AC-2. A duplicate reports the recorded claim_reference."""
    notification = make_notification()
    first = submit_notification(notification, policy_client, repository)
    retry = make_notification()

    second = submit_notification(retry, policy_client, repository)

    assert first.accepted is True
    assert second.accepted is False
    assert second.failure is not None
    assert second.failure.rule == "V-6"
    assert second.failure.code == "DUPLICATE_NOTIFICATION"
    assert second.claim_reference == first.claim_reference
