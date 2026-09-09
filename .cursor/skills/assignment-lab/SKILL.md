---
name: assignment-lab
description: >-
  Reads a claims-intake assignment pack, writes isolated grader subagents from
  the rubric and acceptance criteria, then implements in scoped increments and
  re-grades until every cell is Excellent and every criterion is met. Use when
  working an assignment, scoring a rubric, checking acceptance criteria, or
  aiming for 100 on a lab day.
---

# Assignment lab

Orchestrate a lab day. Do not create one agent that implements until it thinks it scored 100.

Pack vs product, agent naming, and Task launch: [reference.md](reference.md).
Agent file skeletons: [templates.md](templates.md).

## 1. Locate the pack

Default: `claims-intake/docs/assignment-N/assignment/`.

Required: `instructions.md`, `acceptance-criteria.md`, `rubric.md`.
Optional: `feedback.md`.

Product authority stays at `claims-intake/docs/` (`api-contract.md`, `requirements-brief.md`, `payload-triage.md`). `notes/` is never authority.

## 2. Read before writing agents or code

Read instructions, acceptance criteria, and rubric in full. Then only the product sections the instructions name.

Read `articles/` only for method (scoping, test-first, review). Articles are not the spec.

## 3. Author graders, then persist them

Write files under `.cursor/agents/`. Reuse existing files for this assignment if the pack has not changed.

**Protected Day 2 names — do not overwrite:**

- `assignment-acceptance-criteria`
- `rubric-model-specification`
- `rubric-repository-behavior`
- `rubric-test-design`
- `rubric-code-quality`
- `rubric-contract-reconciliation`

New agents: `assignment-N-<slug>` (example: `assignment-3-test-first-evidence`). Gate: `assignment-N-acceptance-criteria`.

**Binary gate.** Every acceptance criterion, every out-of-scope / deliverable check, optional feedback items. Verdict: all met or unmet. No points.

**Cell grader.** One per `##` heading in the rubric. Score only that cell. Copy the Excellent row into the prompt; do not paraphrase it.

Each body lists files to read (pack + named product docs + deliverable source/tests), the Excellent checklist or numbered AC list, **do not edit the codebase**, and the output format. Fill from [templates.md](templates.md).

## 4. Same-session launch

Newly written types may not appear in `Task.subagent_type` until a new chat.

This session: `Task` with `subagent_type: generalPurpose` and the generated prompt as the body.
Next session: use the custom type if it is listed.

## 5. Plan increments from instruction steps

Work in instruction order, not rubric-cell order. Each increment is three sentences:

1. **Outcome** — what will be true; its absence would be obvious.
2. **Authority** — file and section the work must satisfy.
3. **Boundary** — files that must not change. If the contract appears wrong, stop and tell the user rather than editing it.

If the instructions require test-first or a commit of failing tests before implementation, that sequence is the grade. Do not squash tests and implementation. Do not open the implementation file while writing those tests.

Git commits are in-scope only when the assignment grades sequence. See [reference.md](reference.md).

## 6. Implement

Implement in this parent, or spawn a **narrow** `generalPurpose` slice against already-failing tests (outcome, authority, boundary; tests must not be modified).

Never spawn “complete the assignment” or “keep going until Excellent.”

## 7. Grade after an increment

Launch the cell graders that cover what just changed. Launch the AC gate before declaring the lab done.

A “not Excellent” or unmet criterion is a new scoped task, not a reason to keep the same session spinning. Restart if the same misunderstanding is corrected twice.

## 8. Done

Stop only when the gate says **all criteria met** and every cell grader says **Excellent**.
