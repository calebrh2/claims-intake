Deliverable
Merged to trunk: a working, containerized claims intake service with api/routes.py, tests/integration/test_routes.py, a Dockerfile, and a complete README.md.

On the pull request: a description meeting the standard above, and your responses to review.

On your partner's pull request: your review.

In the repository: docs/tool-comparison.md.

Interface contracts fixed
C4. api/routes.py: the HTTP surface, its status code behavior, and the response envelope as served. The Dockerfile and the platform flag. The README.md run instructions.

C5. Branch, commit, pull request, and worktree discipline: branch naming, commit message form, pull request description structure, and the blocking comment convention. Every later week inherits this and none re-teaches it.

Acceptance criteria
Each criterion is met or not met. There is no partial credit within a criterion.

A valid notification returns 201 with a claim reference matching the contract's format.
Each rule V-1 through V-7 can be triggered through HTTP and returns the code and status its contract row specifies.
A payload missing a required field returns 400, not a rule code.
A payload with an extra field is rejected rather than accepted with the field ignored.
Each of the three PolicyLookupFailed reasons returns its distinct 5xx status, and none returns a 4xx.
POLICY_NOT_FOUND returns 422 and is distinguishable in the response from every dependency failure.
Every response the service can produce appears in contract section 6.
Integration tests cover an acceptance, at least one rejection per rule, a parse failure, and all three dependency reasons.
The image builds with an explicit linux/amd64 platform and the service runs from it.
README.md explains the platform flag in the author's own words rather than by restating the command.
A new joiner can follow README.md to a running service without installing anything.
The pull request description states what, why, what to look hardest at, and how it was verified.
Every commit on the branch has a specific imperative subject, and no commit contains a credential, a generated artifact, or an unrelated change.
Every comment left on the partner's pull request is labeled as blocking, a question, or a suggestion.
Every comment marked blocking cites a contract section, an acceptance criterion, or a specific failure it would cause.
Every blocking comment received is resolved or answered with a reason before merge.
The required checks pass on the merged change.
docs/tool-comparison.md states a preference for a named kind of task and gives a reason.