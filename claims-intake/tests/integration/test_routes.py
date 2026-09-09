"""HTTP integration tests for POST /notifications.

These tests exercise the service through the HTTP surface. They do not call
submit_notification. A fixture that returned a shared repository would make
duplicate detection depend on suite order; each test gets a new store.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from claims.api.routes import app, get_policy_client, get_repository
from claims.policy_client import LookupFailureReason, PolicyRecord, StubPolicyClient
from claims.repository import NotificationRepository

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CLAIM_REFERENCE = re.compile(r"^CLM-\d{4}-\d{6}$")


def _payloads_by_id(filename: str) -> dict[str, dict[str, Any]]:
    records = json.loads((DATA_DIR / filename).read_text())
    return {record["id"]: record["payload"] for record in records}


VALID = _payloads_by_id("fnol_valid.json")
INVALID = _payloads_by_id("fnol_invalid.json")


@pytest.fixture
def api() -> Iterator[tuple[TestClient, StubPolicyClient, NotificationRepository]]:
    policy_client = StubPolicyClient()
    repository = NotificationRepository()
    app.dependency_overrides[get_policy_client] = lambda: policy_client
    app.dependency_overrides[get_repository] = lambda: repository
    with TestClient(app) as client:
        yield client, policy_client, repository
    app.dependency_overrides.clear()


def _post(
    client: TestClient,
    body: dict[str, Any] | str,
    *,
    raw: bool = False,
) -> Response:
    if raw:
        assert isinstance(body, str)
        response = client.post(
            "/notifications",
            content=body,
            headers={"Content-Type": "application/json"},
        )
        assert isinstance(response, Response)
        return response
    response = client.post("/notifications", json=body)
    assert isinstance(response, Response)
    return response


def test_accepted_notification_returns_201_with_claim_reference(
    api: tuple[TestClient, StubPolicyClient, NotificationRepository],
) -> None:
    client, _, _ = api
    response = _post(client, VALID["VALID-01"])

    assert response.status_code == 201
    body = response.json()
    assert CLAIM_REFERENCE.match(body["claim_reference"])
    assert body["status"] == "recorded"


@pytest.mark.parametrize(
    ("payload_id", "code", "status", "rule"),
    [
        ("INVALID-01", "POLICY_NOT_FOUND", 422, "V-1"),
        ("INVALID-02", "LOSS_BEFORE_INCEPTION", 422, "V-2"),
        ("INVALID-03", "LOSS_AFTER_EXPIRY", 422, "V-3"),
        ("INVALID-04", "AMOUNT_EXCEEDS_LIMIT", 422, "V-4"),
        ("INVALID-05", "TYPE_NOT_COVERED", 422, "V-5"),
        ("INVALID-07", "POLICY_CANCELLED", 422, "V-7"),
    ],
    ids=["v1", "v2", "v3", "v4", "v5", "v7"],
)
def test_each_rule_returns_contract_code_and_status(
    api: tuple[TestClient, StubPolicyClient, NotificationRepository],
    payload_id: str,
    code: str,
    status: int,
    rule: str,
) -> None:
    client, _, _ = api
    response = _post(client, INVALID[payload_id])

    assert response.status_code == status
    body = response.json()
    assert body["code"] == code
    assert body["detail"]["rule"] == rule
    _assert_actionable_detail(code, body["detail"])


class _CountingPolicyClient:
    """Counts get_policy calls so a rejection cannot hide a second lookup."""

    def __init__(self, inner: StubPolicyClient) -> None:
        self._inner = inner
        self.calls = 0

    def get_policy(self, policy_number: str) -> PolicyRecord:
        self.calls += 1
        return self._inner.get_policy(policy_number)


def test_policy_rule_rejection_looks_up_the_policy_once() -> None:
    """A 422 must use the policy the decision already had. A second lookup
    would not be the values the decision was made on, and a failure on that
    call would turn a rule refusal into a 5xx.
    """
    counting = _CountingPolicyClient(StubPolicyClient())
    repository = NotificationRepository()
    app.dependency_overrides[get_policy_client] = lambda: counting
    app.dependency_overrides[get_repository] = lambda: repository
    try:
        with TestClient(app) as client:
            response = _post(client, INVALID["INVALID-03"])
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "LOSS_AFTER_EXPIRY"
    assert counting.calls == 1


def test_duplicate_notification_returns_409_with_existing_reference(
    api: tuple[TestClient, StubPolicyClient, NotificationRepository],
) -> None:
    client, _, _ = api
    first = _post(client, VALID["VALID-01"])
    assert first.status_code == 201
    recorded = first.json()["claim_reference"]

    second = _post(client, INVALID["INVALID-06"])

    assert second.status_code == 409
    body = second.json()
    assert body["code"] == "DUPLICATE_NOTIFICATION"
    assert body["detail"]["rule"] == "V-6"
    assert body["detail"]["claim_reference"] == recorded
    assert body["detail"]["policy_number"] == INVALID["INVALID-06"]["policy_number"]
    assert body["detail"]["loss_date"] == INVALID["INVALID-06"]["loss_date"]
    assert body["detail"]["claim_type"] == INVALID["INVALID-06"]["claim_type"]


def test_missing_required_field_returns_400_not_a_rule_code(
    api: tuple[TestClient, StubPolicyClient, NotificationRepository],
) -> None:
    client, _, _ = api
    body = dict(VALID["VALID-01"])
    del body["estimated_amount"]

    response = _post(client, body)

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "MALFORMED_REQUEST"
    assert payload["detail"]["problem"] == "required_field_absent"
    assert payload["detail"]["field"] == "estimated_amount"
    assert "rule" not in payload["detail"]


def test_extra_field_is_rejected_rather_than_ignored(
    api: tuple[TestClient, StubPolicyClient, NotificationRepository],
) -> None:
    client, _, _ = api
    body = dict(VALID["VALID-01"])
    body["policy_numbr"] = "MOT-4471"

    response = _post(client, body)

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "MALFORMED_REQUEST"
    assert payload["detail"]["problem"] == "unexpected_field"
    assert payload["detail"]["field"] == "policy_numbr"
    assert "rule" not in payload["detail"]


@pytest.mark.parametrize(
    ("reason", "status", "code"),
    [
        ("timeout", 504, "POLICY_MASTER_TIMEOUT"),
        ("unreachable", 503, "POLICY_MASTER_UNREACHABLE"),
        ("unparsable", 502, "POLICY_MASTER_INVALID_RESPONSE"),
    ],
    ids=["timeout", "unreachable", "unparsable"],
)
def test_policy_lookup_failure_returns_distinct_5xx(
    api: tuple[TestClient, StubPolicyClient, NotificationRepository],
    reason: LookupFailureReason,
    status: int,
    code: str,
) -> None:
    client, policy_client, _ = api
    policy_client.fail_with = reason

    response = _post(client, VALID["VALID-01"])

    assert response.status_code == status
    body = response.json()
    assert body["code"] == code
    assert body["detail"]["dependency"] == "policy_master"
    assert "rule" not in body["detail"]
    if reason == "timeout":
        assert body["detail"]["timeout_ms"] == 2000
    else:
        assert "timeout_ms" not in body["detail"]


def test_policy_not_found_is_422_and_distinct_from_lookup_failure(
    api: tuple[TestClient, StubPolicyClient, NotificationRepository],
) -> None:
    client, _, _ = api
    response = _post(client, INVALID["INVALID-01"])

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "POLICY_NOT_FOUND"
    assert body["detail"]["rule"] == "V-1"
    assert body["detail"]["policy_number"] == "MOT-9999"
    assert "dependency" not in body["detail"]


def test_invalid_json_returns_400_malformed_request(
    api: tuple[TestClient, StubPolicyClient, NotificationRepository],
) -> None:
    client, _, _ = api
    response = _post(client, "{not json", raw=True)

    assert response.status_code == 400
    body = response.json()
    assert body["code"] == "MALFORMED_REQUEST"
    assert body["detail"]["problem"] == "invalid_json"
    assert "field" not in body["detail"]
    assert "rule" not in body["detail"]


def _assert_actionable_detail(code: str, detail: dict[str, Any]) -> None:
    expected = {
        "POLICY_NOT_FOUND": {"rule", "policy_number"},
        "LOSS_BEFORE_INCEPTION": {"rule", "loss_date", "effective_date"},
        "LOSS_AFTER_EXPIRY": {"rule", "loss_date", "expiry_date"},
        "POLICY_CANCELLED": {"rule", "loss_date", "cancellation_date"},
        "AMOUNT_EXCEEDS_LIMIT": {"rule", "estimated_amount", "limit"},
        "TYPE_NOT_COVERED": {"rule", "claim_type", "product"},
    }
    assert expected[code] <= set(detail.keys())
