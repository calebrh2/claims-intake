Git as an Engineering Discipline
Why this matters on an engagement
Something is rejecting valid notifications and it started sometime in the last two weeks. You have a working service, a broken one, and roughly forty commits between them, which is exactly the situation version control was built for. Then you open the log and it reads wip, fixes, more work, fix tests, updates. The commits average four hundred lines and each one touches the rules, the models, and a formatting pass. There is no commit you can revert, because every one of them contains the change you want to remove and three you need to keep. The tooling that should have found this in a few minutes is useless, and you are now reading diffs by hand.

The person that history failed is you, and the person you are writing history for is also you, or your pod partner, on a day when something is broken and nobody is calm. That is the entire argument. Commit discipline is not tidiness and it is not a process requirement somebody imposed. It is the difference between a codebase you can interrogate and one you can only read.

Core concepts
A commit is a unit of change, not a save point. The instinct is to commit when you pause, which produces a history organized by your attention span. What makes history useful is that it is organized by change: one commit does one thing, that thing is complete, and the tests pass at that point. The test is whether the commit could be described in a single sentence without using "and", which is the same test you applied to function names on Tuesday, applied to a different artifact for the same underlying reason. If the commit needs a list to describe, it should have been several commits.

Atomicity is the precondition for every tool that makes history worth having. Revert removes one commit, which is only useful if that commit contains one thing. Bisect finds the commit that introduced a defect by testing halfway points, which only converges to something actionable if each commit is small. Blame tells you which change last touched a line and, through it, why, which is only informative if the commit that touched it was about that line rather than about a reformat that touched everything. Cherry-pick moves one change to another branch, which is impossible if the change is entangled with three others. Four capabilities, one precondition, and the precondition is decided at the moment you type git commit and cannot be recovered afterward.

Staging is a deliberate act, and git add . is how commits stop being atomic. By the time you are ready to commit you usually have more in your working tree than belongs in one change: the rule you implemented, a typo you fixed while you were in there, a debug line you added and removed, a formatting change your editor applied. Adding everything bundles them. Adding deliberately, with git add -p to stage individual hunks, is what lets you commit the rule now and the typo separately, and it has a second benefit that people underrate. Reviewing your changes hunk by hunk as you stage them is a review, and it is the one review guaranteed to happen before the code leaves your machine.

The subject says what changed. The body says why. The subject is one line, written in the imperative as though completing the sentence "this commit will", kept short enough to read in a log listing, and specific enough to be useful on its own. Add V-7 cancellation rule to evaluation order is a subject. Fix bug is not, and neither is Updated service.py, which describes the file rather than the change. The body is where the value is, and it exists to carry what the diff cannot show: the constraint you were working under, the alternative you rejected and why, the acceptance criterion that forced an unobvious choice. A reader can always see what you did by reading the diff. They can never see what you decided not to do.

Record the rejected alternative. This is the single highest value habit in the article and almost nobody does it. When a future engineer looks at a decision that seems wrong, the question in their head is whether the author considered the obvious alternative. If the commit says the alternative was considered and rejected for a stated reason, they either accept it or argue with the reason, and both are productive. If the commit says nothing, they assume it was not considered, and they change it, and they find out why it was rejected the way you would rather nobody found out.

Commit small and push often, because unshared work is invisible risk. Work that lives only on your machine cannot be seen, reviewed, backed up, or built on. It also diverges: every hour your branch is not shared is an hour trunk moves without you, and the reconciliation cost grows faster than the divergence does. Short-lived branches with frequent pushes keep that cost near zero and keep your pod aware of what you are touching. This matters more than usual on this engagement, for a reason the third article today deals with directly: when several people and several agents are producing changes against one repository, the size and frequency of what you land is the main thing determining whether anybody can merge.

Some things never enter a commit, and a later commit does not undo it. Credentials, tokens, connection strings, client data, large generated artifacts, and anything your build produces. The important part is the mechanism: git history is durable and distributed, so once a credential is committed and pushed it exists in every clone, in the reflog, and in anything that mirrored the repository. Deleting it in the next commit removes it from the current state and leaves it in the history, which is where anyone looking for it will look. The only correct response to a committed credential is to treat it as compromised and rotate it. Week 7 covers secrets management as a discipline. What you need today is the rule and the reason it admits no exceptions.

Worked example
The commit that implements the cancellation rule, in full.

Add V-7 cancellation rule before V-3 in evaluation order

Cancelled policies keep their original expiry_date in the policy
master, so a loss inside the original term against a cancelled policy
was being accepted.

Placed before V-3 rather than at the end of the tuple. WI-0158 AC-4
requires that a policy which is both cancelled and out of term reports
POLICY_CANCELLED, because a handler told only that the loss is after
expiry will investigate the wrong system. Ascending identifier order
would have reported LOSS_AFTER_EXPIRY, so section 4.1 of the contract
now states position explicitly rather than deriving it from the
identifier.

Boundary is exclusive: a loss on the cancellation date is not covered
per AC-2. Note this is the opposite of V-2, where cover attaches on
the inception date.

Refs: WI-0158

Almost everything of value here is invisible in the diff. The diff shows a function and a changed tuple. It does not show that the placement was a decision, that ascending order was the obvious approach and was rejected, which acceptance criterion forced it, or that the boundary deliberately disagrees with the rule three lines above it. The last paragraph in particular is written for the engineer who will one day look at two adjacent rules with opposite comparisons and assume one of them is a typo.

The subject stands alone. Read in a log listing with no body visible, it tells you what happened and implies that the ordering was deliberate.

Now the same work, committed two ways.

$ git log --oneline
4e2a1c9 wip
b81f3d2 fix
9c04e77 updates to service and models and tests

$ git log --oneline
7d09b4e Add V-7 cancellation rule before V-3 in evaluation order
a3f21c8 Add failing tests for V-7 cancellation boundary
5f8c012 Add cancellation_date to Policy model

The second history answers questions. Which commit introduced the ordering change, and can it be reverted without losing the model field. Whether the tests preceded the implementation, which is yesterday's discipline made checkable. Where to start bisecting if cancelled policies start behaving oddly. The first history answers none of them, and no amount of care later recovers the information, because the information was never recorded.

Staging is what makes the second version possible. If the model change, the tests, and the rule all landed in your working tree together, git add -p is how they leave it separately.

$ git add -p src/claims/models.py

Stage the cancellation_date field, commit it, then stage the tests, then the rule. Three commits, each complete, each passing, each describable in one sentence.

Failure modes
The subject that says nothing. fix, wip, updates. It costs the author two seconds and it costs every future reader the entire diff. The specific damage is to git log --oneline, which is how anyone orients in an unfamiliar history and which becomes worthless.

The mixed commit. A feature, a rename, and a formatting pass in one change. It cannot be reverted cleanly, it makes bisect land on a commit too large to reason about, and it destroys blame for every line the formatter touched. It is created by git add . and prevented by staging deliberately.

The body that restates the diff. A paragraph explaining that a function was added and a tuple was modified, which the reader can already see. It looks conscientious and carries nothing. If the body does not contain a decision, a constraint, or a rejected alternative, it is not doing work.

The credential fixed in the next commit. The value is gone from the working tree and present in the history, in every clone, forever. The remedy is rotation, and the delay between committing it and admitting it is the entire window in which it can be used.

The branch that grew. Work accumulates unshared, trunk moves, and the merge becomes an event rather than a routine. Nobody could review it well even if they wanted to, and the review that does happen is nominal, which means the change effectively went in unreviewed.

Checklist
[ ] Every commit I made today does one thing and could be described without "and"

[ ] The tests pass at every commit, not only at the end of the branch

[ ] I staged deliberately and read every hunk as I staged it

[ ] Every subject line is imperative, specific, and useful with no body visible

[ ] Every body explains why rather than restating what

[ ] Where I chose between two defensible approaches, the rejected one is recorded with its reason

[ ] Every commit implementing a requirement references its work item

[ ] The failing test for a behavior is in an earlier commit than the behavior

[ ] Nothing generated, nothing large, and no credential entered any commit

[ ] My branch is pushed and is short enough that my pod partner could review it properly