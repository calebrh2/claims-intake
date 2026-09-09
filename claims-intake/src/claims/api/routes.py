"""HTTP surface for the claims intake service.

This layer does three things and no more: it parses the request, it calls the
service, and it maps the outcome to a status code. It holds no rule logic. A rule
that appears here is a rule the service layer cannot be tested for.

Day 4 lab. Implement against `docs/api-contract.md` sections 5 and 6.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Any

from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from claims.models import ErrorCode, NotificationRequest, RuleFailure
from claims.policy_client import (
    LookupFailureReason,
    PolicyClient,
    PolicyLookupFailed,
    PolicyRecord,
    StubPolicyClient,
)
from claims.repository import NotificationRepository
from claims.service import ValidationOutcome, submit_notification

# Contract §5.3 example. The stub has no real wait; the promised key still has
# to be present so a caller can log the budget that expired.
POLICY_MASTER_TIMEOUT_MS = 2000

# Contract section 6: each code maps to exactly one status. Applied here, not
# in the service, because the service returns a code and does not know HTTP.
STATUS_BY_CODE: dict[str, int] = {
    "MALFORMED_REQUEST": 400,
    "DUPLICATE_NOTIFICATION": 409,
    "POLICY_NOT_FOUND": 422,
    "LOSS_BEFORE_INCEPTION": 422,
    "LOSS_AFTER_EXPIRY": 422,
    "POLICY_CANCELLED": 422,
    "AMOUNT_EXCEEDS_LIMIT": 422,
    "TYPE_NOT_COVERED": 422,
    "INTERNAL_ERROR": 500,
    "POLICY_MASTER_INVALID_RESPONSE": 502,
    "POLICY_MASTER_UNREACHABLE": 503,
    "POLICY_MASTER_TIMEOUT": 504,
}

LOOKUP_FAILURE: dict[LookupFailureReason, tuple[str, str]] = {
    "timeout": ("POLICY_MASTER_TIMEOUT", "The policy master did not respond in time."),
    "unreachable": ("POLICY_MASTER_UNREACHABLE", "The policy master could not be reached."),
    "unparsable": (
        "POLICY_MASTER_INVALID_RESPONSE",
        "The policy master answered; this service could not parse it.",
    ),
}

# Process-wide defaults so a running image records duplicates across requests.
# Tests replace these via FastAPI dependency_overrides with a fresh pair.
_default_policy_client: PolicyClient = StubPolicyClient()
_default_repository = NotificationRepository()

app = FastAPI(title="Claims Intake Service")


def get_policy_client() -> PolicyClient:
    return _default_policy_client


def get_repository() -> NotificationRepository:
    return _default_repository


def _envelope(code: str, message: str, detail: dict[str, Any]) -> JSONResponse:
    """Section 5: every non-2xx body is this object and no other."""
    return JSONResponse(
        status_code=STATUS_BY_CODE[code],
        content={"code": code, "message": message, "detail": detail},
    )


def _field_from_loc(loc: tuple[Any, ...]) -> str | None:
    if len(loc) >= 2 and loc[0] == "body" and isinstance(loc[1], str):
        return loc[1]
    return None


def _problem_from_validation(errors: list[dict[str, Any]]) -> tuple[str, str | None]:
    """Map a Pydantic/FastAPI error list onto a section 5.2 problem token.

    The first error is enough: a body can be wrong in several ways and the
    caller sees one reason, the same rule the service uses for V-codes.
    """
    if not errors:
        return "invalid_type", None
    error = errors[0]
    error_type = str(error.get("type", ""))
    field = _field_from_loc(tuple(error.get("loc", ())))

    if error_type in {"json_invalid", "json_decode"} or field is None and "json" in error_type:
        return "invalid_json", None
    if error_type == "missing":
        return "required_field_absent", field
    if error_type == "extra_forbidden":
        return "unexpected_field", field
    if error_type in {"string_too_short", "too_short"}:
        return "empty_value", field
    if error_type == "literal_error":
        return "value_not_in_vocabulary", field
    if error_type == "float_money":
        return "inexact_money", field
    if error_type in {"invalid_scale", "decimal_max_places", "decimal_places"}:
        return "invalid_scale", field
    if error_type in {"greater_than", "greater_than_equal"}:
        return "not_greater_than_zero", field
    if "json" in error_type:
        return "invalid_json", None
    return "invalid_type", field


def _malformed_from_errors(errors: list[Any], fallback_message: str) -> JSONResponse:
    encoded = jsonable_encoder(errors)
    problem, field = _problem_from_validation(encoded)
    detail: dict[str, Any] = {"problem": problem}
    if field is not None:
        detail["field"] = field
    message = fallback_message
    if problem == "invalid_json":
        message = "The body was not valid JSON."
    elif problem == "required_field_absent" and field is not None:
        message = f"Required field {field} is absent."
    elif problem == "unexpected_field" and field is not None:
        message = f"Field {field} is not defined by this contract."
    return _envelope("MALFORMED_REQUEST", message, detail)


def _decimal_wire(value: Decimal) -> str:
    return format(value, "f") if value.as_tuple().exponent == -2 else f"{value:.2f}"


def _rule_detail(
    notification: NotificationRequest,
    failure: RuleFailure,
    outcome: ValidationOutcome,
    policy_client: PolicyClient,
) -> dict[str, Any]:
    """Promised detail keys from section 6. Assembled here because RuleFailure
    carries only rule and code; the values the decision used live on the
    notification and, for most rows, the policy record.
    """
    code = str(failure.code)
    rule = str(failure.rule)
    if code == "POLICY_NOT_FOUND":
        return {"rule": rule, "policy_number": notification.policy_number}
    if code == "DUPLICATE_NOTIFICATION":
        return {
            "rule": rule,
            "claim_reference": outcome.claim_reference,
            "policy_number": notification.policy_number,
            "loss_date": notification.loss_date.isoformat(),
            "claim_type": notification.claim_type,
        }
    record = policy_client.get_policy(notification.policy_number)
    return _policy_rule_detail(code, rule, notification, record)


def _policy_rule_detail(
    code: str,
    rule: str,
    notification: NotificationRequest,
    record: PolicyRecord,
) -> dict[str, Any]:
    if code == "LOSS_BEFORE_INCEPTION":
        return {
            "rule": rule,
            "loss_date": notification.loss_date.isoformat(),
            "effective_date": record.effective_date.isoformat(),
        }
    if code == "LOSS_AFTER_EXPIRY":
        return {
            "rule": rule,
            "loss_date": notification.loss_date.isoformat(),
            "expiry_date": record.expiry_date.isoformat(),
        }
    if code == "POLICY_CANCELLED":
        cancellation = record.cancellation_date
        return {
            "rule": rule,
            "loss_date": notification.loss_date.isoformat(),
            "cancellation_date": None if cancellation is None else cancellation.isoformat(),
        }
    if code == "AMOUNT_EXCEEDS_LIMIT":
        return {
            "rule": rule,
            "estimated_amount": _decimal_wire(notification.estimated_amount),
            "limit": _decimal_wire(record.limit),
        }
    if code == "TYPE_NOT_COVERED":
        return {
            "rule": rule,
            "claim_type": notification.claim_type,
            "product": record.product,
        }
    return {"rule": rule}


def _rule_message(code: ErrorCode) -> str:
    messages = {
        "POLICY_NOT_FOUND": "No policy exists with this number.",
        "LOSS_BEFORE_INCEPTION": "The loss date is before the policy inception date.",
        "LOSS_AFTER_EXPIRY": "The loss date is after the policy expiry date.",
        "POLICY_CANCELLED": "The policy was cancelled before the loss date.",
        "AMOUNT_EXCEEDS_LIMIT": "The estimated amount exceeds the policy limit.",
        "TYPE_NOT_COVERED": "This claim type is not covered on the policy's product.",
        "DUPLICATE_NOTIFICATION": "A notification for this loss event is already recorded.",
    }
    return messages.get(str(code), "The notification was refused.")


@app.exception_handler(RequestValidationError)
async def request_not_interpretable(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    # FastAPI would otherwise return 422 with its own body. Contract §2.4 and
    # §6: an uninterpretable request is MALFORMED_REQUEST at 400, envelope only.
    return _malformed_from_errors(list(exc.errors()), "The request could not be interpreted.")


@app.exception_handler(ValidationError)
async def model_not_interpretable(
    _request: Request,
    exc: ValidationError,
) -> JSONResponse:
    return _malformed_from_errors(list(exc.errors()), "The request could not be interpreted.")


@app.exception_handler(Exception)
async def internal_failure(_request: Request, exc: Exception) -> JSONResponse:
    # Do not swallow parse/lookup exceptions or Starlette HTTP errors.
    if isinstance(
        exc,
        RequestValidationError | ValidationError | PolicyLookupFailed | StarletteHTTPException,
    ):
        raise exc
    return _envelope(
        "INTERNAL_ERROR",
        "This service failed while handling the request.",
        {"service": "claims-intake"},
    )


@app.post("/notifications")
def create_notification(
    notification: NotificationRequest,
    policy_client: Annotated[PolicyClient, Depends(get_policy_client)],
    repository: Annotated[NotificationRepository, Depends(get_repository)],
) -> JSONResponse:
    try:
        outcome = submit_notification(notification, policy_client, repository)
    except PolicyLookupFailed as exc:
        code, message = LOOKUP_FAILURE[exc.reason]
        detail: dict[str, Any] = {"dependency": "policy_master"}
        if exc.reason == "timeout":
            detail["timeout_ms"] = POLICY_MASTER_TIMEOUT_MS
        return _envelope(code, message, detail)

    if outcome.accepted:
        return JSONResponse(
            status_code=201,
            content={
                "claim_reference": outcome.claim_reference,
                "status": "recorded",
            },
        )

    if outcome.failure is None:
        return _envelope(
            "INTERNAL_ERROR",
            "This service failed while handling the request.",
            {"service": "claims-intake"},
        )

    failure = outcome.failure
    return _envelope(
        str(failure.code),
        _rule_message(failure.code),
        _rule_detail(notification, failure, outcome, policy_client),
    )
