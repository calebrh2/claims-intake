Ship the Claims Intake Service
Objective
Turn three days of components into a running, containerized service, merged to trunk through a reviewed pull request.

Everything you need already exists. The contract specifies the behavior, the models guarantee the objects, the rule engine makes the decisions, and the pipeline enforces the standards. What is missing is the HTTP surface that exposes it, the tests that prove it works end to end, the image that carries it, and the review that lets it merge. That last item is not administrative. It is the graded artifact that distinguishes an engineer who produces work from one who can be trusted with a codebase.

This is the whole of Day 4. There is no separate assignment alongside it.

Prerequisites
All three Day 4 articles read.

Components C1 through C3 complete and committed: the contract, the models and repository, the rule engine, and the pipeline.

Your pipeline is green on your branch.

You know which checks are required on the protected branch, confirmed by observation rather than by assumption.

What each day produced
Day	Component	What it fixed
1	C1	docs/api-contract.md: request and response shapes, error envelope, status mapping, rules V-1 through V-7, evaluation order
2	C2	models.py and repository.py: the objects, their constraints, recording and duplicate detection
3	C3	service.py: evaluate_notification, submit_notification, the propagation rule for PolicyLookupFailed, and checks.yaml
4	C4, C5	The HTTP surface, the image, and the branch, commit, pull request, and worktree discipline every later week inherits
If a component is incomplete, finish it before starting the lab. Integration does not paper over a missing part, it exposes it.

Setup
Work from your own branch off trunk. Where you run more than one agent, each gets its own worktree under .worktrees/, which is inside the mounted repository path and is ignored by git.

Before starting, list the files each parallel task may modify and confirm no two of them intersect. api/routes.py and tests/integration/test_routes.py are separate surfaces and can proceed in parallel. The Dockerfile and README.md are separate again. Nothing in this lab requires two concurrent tasks to edit one file, and if your plan produces one, change the plan.

Mock data
Everything is synthetic and ships in the starter repository. No real client data and no named clients.

data/policies.json holds around forty personal lines policies, each with policy_number, product, effective_date, expiry_date, cancellation_date, limit, and permitted claim types. The set includes recently expired policies, policies incepting shortly, cancelled policies, and policies whose limits sit exactly on a boundary a test will probe.

data/fnol_valid.json, data/fnol_invalid.json, and data/fnol_edge.json hold notification payloads. The valid set passes every rule. The invalid set fails exactly one rule each. The edge set is the twelve payloads you triaged on Day 1, and it is the source for your integration cases.

StubPolicyClient reads policies.json and can be configured to raise PolicyNotFound, or PolicyLookupFailed with any of its three reasons. It is how you exercise the dependency boundary without a dependency.