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
from claims.policy_client import PolicyLookupFailed, StubPolicyClient
from claims.service import (
    evaluate_amount_within_limit,
    evaluate_claim_type_covered,
    evaluate_loss_after_inception,
    evaluate_loss_before_expiry,
    evaluate_policy_exists,
    evaluate_policy_not_cancelled,
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
