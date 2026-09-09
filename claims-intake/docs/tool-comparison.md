# Tool comparison

This lab was done in Cursor. Fill this in from a task you actually performed
on Day 4. The comparison is what is graded, not the code. An answer that says
both tools are good is not an answer.

## Task in scope

The bounded task this comparison is about (pick one and keep it specific):

- Mapping `POST /notifications` onto contract section 6 (parse failures, rule
  codes, and the three `PolicyLookupFailed` reasons), or
- Writing `tests/integration/test_routes.py` so the suite hits HTTP rather
  than `submit_notification`.

**Your task (one sentence):**

>

## What Cursor made easy

Talking points — replace with what you actually noticed:

- Having the contract, `routes.py`, and `service.py` in context while choosing
  status codes.
- Generating a first cut of the envelope mapping or the TestClient fixture.
- Jumping between a section 6 row and the handler that must implement it.

**Your notes:**

>

## What Cursor made awkward

Talking points — replace with a real friction, not a generic limitation:

- Confident-sounding mapping that still used FastAPI's default 422 body
  instead of `MALFORMED_REQUEST` at 400.
- Detail keys that look complete until you check the promised-keys table
  (for example `timeout_ms` only on timeout, `rule` never on a lookup
  failure).
- Integration tests that imported `submit_notification` and never opened a
  socket, which would fail the "through HTTP" requirement if you accepted
  them uncritically.
- Placeholder prose in this file or the README platform note: the tool can
  write fluent copy that is not *your* words, which the rubric rejects.

**Your notes:**

>

## Preference

State which kind of work you would take to Cursor and which kind you would
take to another tool (your usual agent, the editor, tests first by hand),
and **why**. Name the kind of task. "I would use both" does not meet the
criterion.

**Your preference and reason:**

>
