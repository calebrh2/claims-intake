Scoping Work for an Agent
Why this matters on an engagement
You ask for the validation rules to be implemented. What comes back is seven rule functions, a refactor of models.py that you did not request, a new helper module you have never heard of, an edit to docs/api-contract.md that changed a status code, and a passing test suite. All of it is plausible and some of it is good. You now own every line, including the contract change you have not noticed yet, and reviewing it properly will take longer than writing the rules yourself would have. The work was not done badly. It was scoped badly, and the scoping was your job.

The instinct that causes this is a reasonable one: you give a capable colleague a goal rather than a set of instructions, because treating them as a machine wastes them. An agent is not that colleague. It has no stake in the codebase, no memory of Tuesday's decision, and no sense of which files are load bearing, and it will confidently expand into any space you leave open. The skill you are building today is stating a task so precisely that the result is either what you asked for or obviously not, because that is the only version of this that stays faster than doing it yourself once review is counted.

Core concepts
Three controls, and they are not the same control. What the agent can see is context. What it is permitted to do is authority. Whether to keep going is session management. People collapse these into one idea of trust, and the collapse produces bad decisions in both directions: an agent given broad authority because the task is simple, or an agent starved of context because the task is sensitive. They are independent dials. A task can warrant a lot of context and almost no authority, which is the shape of most analysis work. It can warrant narrow context and real authority, which is the shape of a well specified implementation. Decide each one separately and you will find that most of the anxiety about agentic work is actually about the second dial, and that the second dial is the one you have the most direct control over.

A task statement names an outcome, an authority, and a boundary. The outcome is what will be true when the work is done, stated so that its absence would be obvious. The authority is the document the work must satisfy, which on this engagement is your contract, a work item, or a failing test. The boundary is what must not change. That third element is the one people leave out, and it is the one that prevents the opening scenario, because an agent that has not been told which files are out of scope treats every file as in scope. A statement carrying all three is usually three sentences and it is the single highest return habit in this article.

Context is a budget, and file reads spend most of it. Everything the agent knows about your task occupies a finite window: your instructions, the files it has read, the output of commands it has run, and the conversation so far. When that budget fills, quality degrades in a way that is hard to see from the outside, because the responses stay fluent. The largest single consumer is exploration. An agent told to implement the rules will read the whole source tree looking for where they belong, and most of what it reads is irrelevant. An agent told that the rules go in src/claims/service.py, that the models are in src/claims/models.py, and that the specification is section 4.2 of the contract has spent almost nothing and knows more. Specificity is not politeness or ceremony. It is the mechanism by which you keep the useful material in the window and the noise out of it.

Standing instructions carry conventions. Per-task instructions carry the task. Anything that is true for every piece of work on this repository belongs in a project instruction file that the agent reads at the start of every session: the vocabulary comes from the contract, money is a decimal type, tests are parametrized with named ids, the rule identifiers are V-1 through V-7. Putting those in every prompt wastes your attention and theirs. What belongs in the task is what is specific to this task. The practical benefit is that when you find yourself typing the same correction twice, you have found something that belonged in the standing file, and moving it there is a permanent fix rather than a repeated one.

Context is not enforcement, and confusing the two is where people get hurt. An instruction in context makes an outcome more likely. It does not make the opposite impossible. Telling the agent not to modify the contract reduces the chance it will, and the thing that actually tells you whether it did is your version control diff. Telling it that money is a decimal reduces the chance of a float, and the thing that catches a float is your type checker. This is the reason yesterday's work matters today: strict type checking, a linter, and a test suite are enforcement, and they do not care what was in the prompt. The correct mental model is that you write instructions to shape the output and you rely on gates to verify it, and any belief that survives only because the instruction was clear is a belief you have not checked.

Scope to something you can verify, or the task is not ready to hand over. Before you delegate, state how you would know the result is correct. If the answer is that you would read it and see whether it looks right, the task is underspecified and you have set yourself up to accept plausible work. If the answer is that a named test currently fails and would pass, or that a specific payload currently returns the wrong status and would return the right one, then the task is ready and the review has something to check against. This is also the reason today's assignment has you write the test first: a failing test is the most precise task statement available, because it is unambiguous, it is checkable by something other than your judgment, and it cannot be satisfied by a description of a solution.

Know when to abandon a session rather than continue it. A session that has gone wrong is carrying the wrong context: an incorrect assumption it made early, a file it misread, a fix it applied that you then reverted. Continuing means every subsequent response is conditioned on that material, and the usual experience is a sequence of corrections that each half-work. The signals are consistent and worth learning to notice: you have corrected the same misunderstanding twice, the changes are growing rather than converging, or you have started explaining rather than specifying. When you see them, discard the session, keep whatever was genuinely good, and restate the task with what you have learned. Restarting feels like losing progress and is almost always cheaper than the alternative, because a fresh session with a better task statement starts from your best current understanding rather than from the accumulated wreckage of your first one.

Worked example
The same work, requested two ways.

Implement the validation rules for the claims service.

This is the request that produced the opening scenario. It names no outcome that could be checked, no authority, and no boundary. Every decision it does not make will be made for you, including where the rules live, what they return, what happens when several fail, and whether adjacent files should be tidied while the agent is in there.

Implement rules V-2 through V-5 in src/claims/service.py.

Each rule is a separate function returning RuleFailure or None, following
the pattern of evaluate_policy_exists, which is already written. Conditions,
codes, and boundary behavior come from docs/api-contract.md section 4.2.
Ordering comes from section 4.1.

The failing tests in tests/unit/test_validation.py define correct behavior.
All twelve currently fail. They must all pass and no test may be modified.

Do not change models.py, repository.py, policy_client.py, or anything in
docs/. If the contract appears wrong, stop and tell me rather than editing it.

Read what each part is doing. The first paragraph fixes the outcome and the shape, and it points at an existing function so the pattern does not have to be described. The second names the authority, which is your contract, so the agent is not inventing boundary behavior it has no basis for. The third makes the result verifiable by something that is not your opinion, and forbids the failure mode where a test is adjusted to match the implementation. The fourth is the boundary, and its last sentence is the most valuable line in the statement: it converts a disagreement into a conversation instead of a silent edit to the document everything else depends on.

Notice what is absent. There is no explanation of what a validation rule is, no restatement of the seven conditions, and no description of Pydantic or the domain. All of that is either in the files named or is a standing convention. The statement is short because it is specific, which is the relationship people expect to run the other way.

The operating details of your agent, meaning session commands, permission settings, and the format of the standing instruction file, are in the vendor documentation. Work through it on your own. It changes faster than any article could track, and the judgment in this one is what remains true across versions of it.

Failure modes
The task that names a mechanism instead of an outcome. Asking for a helper function to be added, rather than for a behavior to hold, hands over the wrong decision. You have chosen the implementation and left the correctness open, which is the reverse of what you wanted.

Letting the agent discover the codebase. With no files named, the search happens anyway and it happens inside your context budget. The work then proceeds with a window mostly full of files that had nothing to do with the task, and the degradation this causes is invisible because the output remains fluent.

Treating an instruction as a guarantee. The prompt said not to touch the contract, so the contract was not checked, and the contract was touched. This is not a failure of the instruction, it is a category error about what instructions do. The diff is the check.

Scope you cannot verify. Handing over work you would assess by reading it means you will accept it if it reads well, and generated work always reads well. If you cannot say what would prove it correct before you delegate, you are not delegating, you are outsourcing the decision about whether it is done.

The session you should have abandoned. Three corrections in, each one partially landing, and the surface area of the change is still growing. Every additional turn is conditioned on the material that caused the problem. The cost of continuing is invisible and the cost of restarting is obvious, which is why people continue.

Checklist
[ ] My task statement names an outcome whose absence would be obvious

[ ] It names the authority the work must satisfy, by file and section

[ ] It names what must not change, and says to stop rather than edit if that seems wrong

[ ] I named the files the work needs instead of leaving them to be found

[ ] Nothing in my prompt is a convention that belongs in the standing instruction file

[ ] I have not repeated a correction I already gave in this repository

[ ] I can state what would prove the result correct without reading it and forming an impression

[ ] Every constraint I care about is checked by something, not only stated

[ ] I decided context and authority separately rather than as one judgment about trust

[ ] If I have corrected the same misunderstanding twice, I restarted instead of continuing