# Claims Intake Service

The claims intake service accepts a first notice of loss from the claims
portal, validates it against the policy master and the rule table in
`docs/api-contract.md`, and either records a notification and issues a claim
reference or refuses the submission with a specific reason.

`POST /notifications` is the HTTP surface. A well-formed, admissible
notification returns `201` with a `claim_reference`. Everything else returns
the error envelope in contract section 5, with the status that section 6
assigns to that code.

## Where things are

| Path | What it holds |
| --- | --- |
| `docs/api-contract.md` | What the service accepts, returns, and refuses. The authority. |
| `docs/requirements-brief.md` | The open work items and their acceptance criteria. |
| `docs/payload-triage.md` | Day 1 classification of the edge payloads. |
| `docs/assignment-N/` | That day's instructions, acceptance criteria, rubric, and articles. See `docs/README.md`. |
| `data/` | Synthetic policies and notification payloads. |
| `src/claims/` | The service. |
| `src/claims/api/routes.py` | The HTTP mapping. |
| `tests/` | Unit tests mirror `src/claims/`. Integration tests exercise HTTP. |
| `Dockerfile` | Image that runs the service. |

## Working in this repository

You are inside a Linux container. Confirm it before you start:

```
uname -sm     # Linux aarch64
pwd           # /workspaces/claims-intake
```

Dependencies are already installed. There is no install step. If a tool you
need is missing, that is a defect in the image specification and should be
reported rather than worked around.

Commands below assume the current directory is this project (`claims-intake/`,
the directory that contains `pyproject.toml`).

## Run the service

From this directory:

```
uv run uvicorn claims.api.routes:app --host 0.0.0.0 --port 8000
```

The process listens on port 8000. Submit a notification:

```
curl -sS -X POST http://127.0.0.1:8000/notifications \
  -H 'Content-Type: application/json' \
  -d '{"policy_number":"MOT-4471","loss_date":"2026-04-02","claim_type":"collision","estimated_amount":"4200.00","description":"Rear ended at a junction."}'
```

A valid payload returns `201` and a `claim_reference` matching `CLM-YYYY-NNNNNN`.

## Run the tests

```
uv run pytest
uv run ruff check src tests
uv run mypy
```

`tests/unit/` calls the models, repository, and rule engine as functions.
`tests/integration/test_routes.py` sends HTTP requests; it does not call
`submit_notification` directly.

## Build the image

Build for the architecture the service is deployed on, not the architecture of
this lab container:

```
docker buildx build --platform linux/amd64 -t claims-intake .
```

Run the image:

```
docker run --rm -p 8000:8000 claims-intake
```

The same `curl` as above talks to the process inside the image.

### Why `--platform linux/amd64`

**Author notes — write this section in your own words before review.** The
rubric scores whether the explanation shows you understand why the host and
the target differ, not whether you restated the command.

Talking points to cover:

- What `uname -sm` reports in this lab container, and what architecture the
  deployment target uses.
- What image `docker build` produces if you omit `--platform`, and where that
  image can (and cannot) run.
- What `buildx` is doing that a plain `docker build` on this host would not.
- A concrete failure a new joiner would hit if they shipped an arm64 image to
  an amd64 runtime (or the other way around).
- Why "the flag sets the platform to linux/amd64" is not an explanation of the
  reason the flag exists.

Do not paste the command back as the explanation.

## Data

Everything in `data/` is synthetic and was authored for this program. It
contains no real client data and no named clients.
