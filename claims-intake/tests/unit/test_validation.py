"""Rule-boundary tests for Day 3 validation.

Written against `docs/api-contract.md` section 4 and the work-item acceptance
criteria in `docs/requirements-brief.md`. Each parametrized case names a
comparison on one side of a boundary, on the boundary, or an absence criterion.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

import pytest

from claims.models import NotificationRequest, Policy, RuleFailure
from claims.service import evaluate_loss_after_inception, evaluate_policy_not_cancelled


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
