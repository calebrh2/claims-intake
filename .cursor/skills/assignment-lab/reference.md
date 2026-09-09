# Assignment-lab reference

## Pack vs product

See [claims-intake/docs/README.md](../../../claims-intake/docs/README.md).

| Kind | Path | Role |
| --- | --- | --- |
| Pack | `claims-intake/docs/assignment-N/assignment/` | What this day asks and how it is graded |
| Product | `claims-intake/docs/api-contract.md` | Service authority |
| Product | `claims-intake/docs/requirements-brief.md` | Work items |
| Product | `claims-intake/docs/payload-triage.md` | Edge classification and later notes |
| Method | `claims-intake/docs/assignment-N/articles/` | How to work; not the spec |
| Scratch | `claims-intake/docs/assignment-N/notes/` | Never authority |

`docs/agent-log.md` is a product record when the assignment produces it.

## Agent naming

New graders: `assignment-N-<slug>` in `.cursor/agents/assignment-N-<slug>.md`.

Do not overwrite these Day 2 files:

- `assignment-acceptance-criteria`
- `rubric-model-specification`
- `rubric-repository-behavior`
- `rubric-test-design`
- `rubric-code-quality`
- `rubric-contract-reconciliation`

Reuse `assignment-N-*` files when they already exist and the pack is unchanged.

## Task launch

This chat: `Task` `subagent_type: generalPurpose`, prompt = the agent file body (system prompt plus “score now”). Newly written custom types often are missing from the enum until a new conversation.

Next chat: `subagent_type` equal to the agent `name` if listed.

Launch several graders in parallel. They must not edit the repo.

## Git commits

Commits are in-scope only when the assignment grades sequence (for example Day 3: failing tests committed before the matching implementation). Then follow that order in the history. Do not squash tests and implementation. Do not commit when the pack does not grade history.
