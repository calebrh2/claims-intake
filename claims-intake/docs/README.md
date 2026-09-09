# Docs layout

Two kinds of document live here. Keep them apart.

**Product authority** stays at this directory. Code, tests, and every later assignment point at these paths. Do not copy them into a day’s folder.

| Path | Role |
| --- | --- |
| `api-contract.md` | What the service accepts, returns, and refuses |
| `requirements-brief.md` | Open work items and their binary acceptance criteria |
| `payload-triage.md` | Edge-payload classification and later reconciliation notes |

Day 1 produced the product files above. There is no `assignment-1/` pack in this repo. Day 3’s `docs/agent-log.md` is also a product record when it exists, not part of the graded pack.

**Assignment packs** live in `assignment-N/`. Each pack is what that day asks you to do and how it is graded. It is not the service specification.

```
docs/assignment-N/
  assignment/     # the graded pack — stable filenames
    instructions.md
    acceptance-criteria.md
    rubric.md
    feedback.md   # optional instructor notes
  articles/       # required reading, not graded
  notes/          # optional working notes; not a deliverable
```

Current packs:

```
docs/assignment-2/
  assignment/instructions.md
  assignment/acceptance-criteria.md
  assignment/rubric.md
  assignment/feedback.md
  articles/          # Day 2 articles are not in this repo
  notes/W1-02-requirements.md
  notes/w1-02-requirements-plan.md

docs/assignment-3/
  assignment/instructions.md
  assignment/acceptance-criteria.md
  assignment/rubric.md
  articles/scoping-work-for-an-agent.md
  articles/test-first-in-agentic-flow.md
  articles/reviewing-code-not-yours.md
  notes/
```

A skill or grader should read `assignment-N/assignment/` first, then the product files the instructions name. Do not treat `notes/` as authority when it disagrees with `assignment/` or the contract.
