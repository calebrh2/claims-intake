Reviewing Code You Did Not Write
Why this matters on an engagement
The change was seventy lines of rule functions, it was clean, the tests passed, and you approved it in four minutes because nothing in it looked wrong. Three weeks later the policy master has a slow afternoon and the claims team is told that eleven policies do not exist. They spend two days searching a system of record for policies that are sitting right there, because a single except clause in the code you approved treats a timeout and a genuine absence as the same event. You read that line. It looked like error handling.

This is the review problem in its actual shape. You will not be catching code that looks bad, because you will not often see code that looks bad. You will be deciding whether code that looks entirely reasonable is correct, on material you did not write, at a pace that assumes most of it is fine. Getting good at that is a specific skill with a specific method, and it is different from the reading you have done before, because the thing you are reading has different failure characteristics from anything a person would have handed you.

Core concepts
You are accountable for every line you merge, and there is no version of this where you are not. The engagement does not distinguish between code you typed and code you accepted. When a defect reaches the client, the questions are what it does, why it does that, and who approved it, and the answer to the third question is your name. This is not a moral point, it is a practical one that determines how you spend your attention: if you are going to be answerable for it anyway, the cheapest moment to understand it is now, while the context is loaded and the change is small.

Generated code fails differently from human code, and the difference removes your usual signals. When a person hands you work, its texture is information. Rushed naming in one function suggests the author was tired there. An awkward construction suggests a constraint you have not understood. Inconsistent style suggests two authors or a late edit. You read that gradient without thinking about it and it directs your attention. Generated code has no gradient. It is uniformly fluent, uniformly idiomatic, and uniformly confident, including in the one function that is subtly wrong, and it will produce a complete and well organized implementation of the wrong rule as readily as the right one. The consequence is that you cannot rely on something looking off, because nothing will look off. You have to go looking on purpose.

Read in order of consequence, not in the order the diff presents. A diff is ordered by file path, which is arbitrary with respect to risk. Reviewing top to bottom spends your freshest attention on whatever happens to sort first and your most tired attention on whatever sorts last. Instead, decide before you start what would be worst if it were wrong, and read that first. On this service the order is roughly: anything that decides whether a notification is accepted, anything that maps a condition to an error code or status, anything that touches the boundary with the policy master, and then everything else. The last category is where most of the lines are, and it is correctly where the least of your attention goes.

Check against the authority, not against plausibility. The question is never whether a rule looks right. It is whether it matches the contract line it implements, including the boundary direction, the code it returns, and its position in the evaluation order. That means reading with the contract open, comparing row by row, and it is slower than reading the code alone by a factor that feels indulgent right up until the first time it catches an inverted comparison. Plausibility checking cannot catch a wrong boundary, because both directions are equally plausible in the abstract. Only the specification distinguishes them, and only if you actually consult it.

Learn the specific things this kind of code gets wrong. They recur, and knowing the list converts review from general vigilance into a search. Scope quietly widens beyond the task, so files you did not expect appear in the diff. Behavior gets invented for cases the specification never addressed, and it will be reasonable and undocumented. Boundary comparisons come out inverted, because the natural language description supports both readings. Error handling collapses distinct conditions into one, because a single broad except is idiomatic and shorter. Tests get shaped to match the implementation rather than the requirement, so they pass and prove nothing. Any of these will be present in code that reads well.

A diff shows you what was written and hides what was not. This is the hardest part of the method, because absence has no line number. A rule that was omitted from the ordered tuple does not appear as a change. An error path that was never handled produces no red text. A case in the specification that nobody implemented looks identical to a case that did not exist. The only defense is to review against the specification rather than only against the diff: walk the contract's rule table and confirm each row has an implementation, walk the boundary conditions and confirm each has a path. This is also why the previous article insisted on scoping to something verifiable, because a failing test that stays red is absence made visible.

If you cannot explain it, do not merge it. Not "cannot explain it yet, will look into it after." The state where a merged line does something you could not account for is exactly the state you were in before the two day search described above. When you hit something you do not understand, you have three good options and one bad one. Ask the agent to explain it and verify the explanation against the code, which is faster than it sounds. Rewrite that part yourself. Discard it and restate the task with what you now know. The bad option is approving it because the tests pass, since the tests were quite possibly written by the same process that wrote the code.

Worked example
A generated implementation of two rules, plus the ordering tuple. It is complete, it is idiomatic, and every test in the suite passes.

def evaluate_loss_before_expiry(notification, policy):
    """V-3. The loss must fall within the policy term."""
    if notification.loss_date >= policy.expiry_date:
        return RuleFailure("V-3", "LOSS_AFTER_EXPIRY")
    return None


def resolve_policy(policy_number, client):
    """Fetch the policy for evaluation."""
    try:
        return client.fetch(policy_number)
    except Exception:
        return None


POLICY_RULES = (
    evaluate_loss_after_inception,
    evaluate_loss_before_expiry,
    evaluate_amount_within_limit,
    evaluate_claim_type_permitted,
    evaluate_not_duplicate,
)

Read it in order of consequence rather than in the order it appears.

The highest consequence item is the boundary at the policy master, because that is where a wrong answer becomes a false statement about the client's data. resolve_policy catches Exception and returns None. That single line erases the distinction you built the entire interface around: PolicyNotFound and PolicyLookupFailed both become an absent policy, so a timeout is reported to the claims team as POLICY_NOT_FOUND, which is the two day search. It also swallows anything else that could go wrong, including a defect in your own code, and reports it as a missing policy. Nothing about the line looks alarming. Broad exception handling that returns a safe default is a shape you have seen a thousand times.

Next in consequence is the decision logic. V-3 uses >=, so a loss occurring on the expiry date is rejected. Your contract says the boundary is inclusive and cover runs to the end of the term. The comparison is wrong by one operator, both operators are plausible, and the docstring is accurate about the rule's purpose while the code is wrong about its boundary. This is the defect that plausibility checking cannot find, and the only way to catch it is with section 4.2 open beside the diff.

Then read for absence. The tuple contains five rules. Your contract has seven, and evaluate_policy_exists is legitimately absent because it short circuits before the ordered evaluation. That leaves one missing, V-7 for cancelled policies, and it is missing in the most invisible way available: not as a broken function but as a function that is simply not in the list. The tests pass because there is no test for a rule nobody implemented. Nothing in the diff is red. You find this by walking your contract's rule table and asking, for each row, where it is, which takes about ninety seconds and is the only technique that works.

Three defects. One of them will produce a client-facing incident, one will reject valid claims on a specific day of every policy term, and one means a rule the business asked for does not exist. All of it reads well.

Failure modes
Approving because nothing looked alarming. The default outcome of reading generated code without a method. Absence of alarm is not evidence, because the code is fluent by construction. The review needs a positive claim, which is that you checked specific things against a specific document, rather than the negative claim that nothing caught your eye.

Reading in diff order. Attention is a budget that declines through a review, and diff order spends it on whatever sorts alphabetically first. Decide the risk order before you open the change, then read that way regardless of how the change is presented.

Checking plausibility instead of the specification. The most common failure among strong engineers, because they can tell whether code is sensible and that skill is genuinely useful elsewhere. It cannot distinguish an inclusive boundary from an exclusive one, and boundaries are where the defects concentrate.

Reviewing only what changed. The diff is the wrong unit for completeness. Everything that should exist and does not is invisible in it, and omissions are the most expensive category to find later, because there is no failing test pointing at them.

Deferring understanding past the merge. The line goes in with a note to revisit it, and the revisit does not happen, and it is now load bearing. The moment of maximum context is right now, and it will never be this cheap to understand again.

Checklist
[ ] I decided the risk order before reading, and read that way rather than in diff order

[ ] Every rule in the change was compared against its contract row, with the contract open

[ ] Every boundary comparison was checked for direction, not just for presence

[ ] Every exception handler distinguishes the conditions my interface distinguishes

[ ] No handler catches broadly enough to swallow a defect in my own code

[ ] I walked the contract's rule table and confirmed each row has an implementation

[ ] I walked the boundary conditions and confirmed each has a path

[ ] Nothing outside the scope I set appears in the diff, and anything that does was deliberate

[ ] The tests assert the requirement rather than the implementation that was just written

[ ] There is no line in this change I could not explain to my Senior FDE right now