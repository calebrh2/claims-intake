Test-First in an Agentic Workflow
Why this matters on an engagement
Take the inverted boundary from the previous article, the one where V-3 rejects a loss occurring on the expiry date. Now imagine you had written a test for it afterward, the way most people write tests. You would have opened the implementation to see what it does, noticed it compares with >=, and written a case asserting that a loss on the expiry date is rejected. The test would pass. It would be a well named, parametrized, thoroughly conventional test, and it would have locked the defect in place and made it harder to fix, because now anyone who corrects the operator breaks a test and has to decide whether the test or the code is the authority.

That is not a hypothetical failure mode, it is the normal outcome of writing tests last, and it gets worse rather than better when an agent is involved, because the volume of code you are checking goes up while the amount you wrote yourself goes to nearly zero. Test-first is usually sold as a design practice. On this engagement its value is narrower and sharper: it is the only way to be certain that what you are checking against came from the requirement rather than from the code.

Core concepts
A test written after the implementation can only confirm the implementation. The mechanism is not laziness or bad faith, it is unavoidable. To write the test you read the code, and once you have read it you know what it does, and what it does becomes the thing you assert. Every ambiguity in the requirement has already been resolved by the implementation, and you inherit the resolution without noticing you made a choice. This is why after-the-fact tests are so reliably green on the first run, which people take as evidence of good code and which is actually evidence that the test learned from the code. A test that has never been red has demonstrated nothing.

Write the test from the requirement, while the implementation does not yet exist. The source is the contract row and the acceptance criterion, not the source file. With nothing to read, there is nothing to copy, and every decision the requirement failed to make becomes visible as a question you cannot answer. That is the design benefit people talk about, and it arrives here as a practical one: the ambiguities surface now, while fixing them means editing a document, rather than on Thursday when it means changing code that other code depends on. If you cannot write the test because the requirement does not determine the answer, you have found a defect in your contract, and that is a good morning's work.

A failing test is the most precise task statement available. The previous article said to scope work to something verifiable. A red test is the strongest form of that. It is unambiguous, because it either passes or does not. It is checkable by something that is not your judgment, which matters because your judgment is exactly what fluent generated code is good at satisfying. And it cannot be met by a plausible description of a solution, which is the failure mode of every task statement written in prose. Handing over a failing test with an instruction not to modify it is the tightest specification you can give.

Red has to be red for the right reason. A test that fails because the function does not exist yet, or because the stub raises NotImplementedError, has told you nothing about your assertion. It might be asserting the wrong field, comparing against a value that can never occur, or checking a condition that is true regardless. Run it and read the failure. You want to see the assertion you care about fail, with the values you expected, so that when it later turns green you know the transition was caused by the behavior rather than by the code merely existing. This costs one extra run and it is the difference between a test you have verified and a test you have written.

The order is visible in the history, which is what makes it gradeable. Nothing about a finished branch reveals whether the test came first. Both orderings produce the same files. What distinguishes them is the sequence of commits: the failing test, then the implementation that turns it green. Committing in that order is not bookkeeping, it is the only durable evidence the sequence happened, and it is what lets a reviewer see that the specification preceded the solution rather than being reverse engineered from it. Tomorrow you will look at commits as an engineering artifact in their own right. Today what matters is that you commit the red test before you write the code that fixes it.

Test-first protects the sequence, not the specification. Be clear about what you are buying, because people oversell this. It does not tell you whether the requirement is right. It does not find the case nobody thought of, so a rule with an unconsidered boundary produces a test with the same gap. It does not help if you assert the wrong thing confidently. And it collapses entirely if you ask the same session to write both the test and the implementation from the same loose prompt, because then both artifacts share one interpretation and agreement between them means nothing at all. The protection is specifically this: what you check against came from the requirement, and the requirement existed before the solution. Everything else still requires you to think.

Worked example
Building V-7, the cancellation rule, from WI-0158. Nothing exists yet except the stub.

First the test, written with the work item open and service.py closed.

@pytest.mark.parametrize(
    ("cancellation_date", "loss_date", "expected"),
    [
        (date(2026, 6, 1), date(2026, 5, 31), None),
        (date(2026, 6, 1), date(2026, 6, 1), "POLICY_CANCELLED"),
        (date(2026, 6, 1), date(2026, 6, 2), "POLICY_CANCELLED"),
        (None, date(2026, 6, 1), None),
    ],
    ids=[
        "day_before_cancellation_is_covered",
        "cancellation_date_itself_is_not_covered",
        "after_cancellation_is_not_covered",
        "uncancelled_policy_is_unaffected",
    ],
)
def test_v7_ends_cover_at_the_cancellation_date(
    motor_policy, cancellation_date, loss_date, expected
):
    """WI-0158 AC-1, AC-2, AC-3. Cancellation takes effect at the start
    of the cancellation date, so a loss on that date is not covered."""
    policy = motor_policy.model_copy(update={"cancellation_date": cancellation_date})
    notification = a_notification(loss_date=loss_date)

    failure = evaluate_policy_not_cancelled(notification, policy)

    assert (failure.code if failure else None) == expected

Everything in that test came from the work item. The boundary case exists because AC-2 states it explicitly, and note that it points the opposite way from inception, where cover attaches on the day. An implementation written first would very likely have made cancellation inclusive to match V-2, and a test written afterward would have confirmed it. Written this way, the two boundaries disagree because the business says they disagree.

The fourth case exists because AC-3 says the rule does not apply when the field is absent. That case is the one most likely to be skipped by someone testing after the fact, since an implementation that handles None correctly gives you no reason to think about it.

Now run it before writing anything.

E   NameError: name 'evaluate_policy_not_cancelled' is not defined

That is red for the wrong reason. It tells you the function is missing, which you knew. Add the stub, run again, and you get the failure that is actually evidence.

FAILED test_v7_ends_cover_at_the_cancellation_date[cancellation_date_itself_is_not_covered]
E   AssertionError: assert None == 'POLICY_CANCELLED'

Now the assertion has been exercised. The named case tells you which boundary is unsatisfied and the values tell you the test is comparing the right things. This is the point at which the test is worth handing over.

Implement evaluate_policy_not_cancelled in src/claims/service.py and add it
to POLICY_RULES in the position section 4.1 requires.

The four cases in tests/unit/test_validation.py::test_v7_ends_cover_at_the
_cancellation_date define correct behavior. All four currently fail. They
must pass and the test must not be modified.

Do not change any other rule function, the models, or the contract.

Then the history, which is the part a reviewer can actually check.

a3f21c8  Add failing tests for V-7 cancellation boundary
7d09b4e  Implement V-7 and place it before V-3 in evaluation order

Two commits, in that order, and the sequence is now a fact about the branch rather than a claim about your process. A reviewer who wants to know whether the specification preceded the solution reads the log rather than taking your word for it.

Failure modes
The test written from the implementation. The defect is confirmed rather than caught, and it is now protected, because fixing the code breaks a test and the next person has to adjudicate between them. This is the single most common way a thorough-looking suite ends up guaranteeing the wrong behavior.

Red for the wrong reason. The test failed because nothing existed, the code was written, the test went green, and nobody ever saw the assertion itself fail. An assertion that has never failed has not been verified, and it can quietly be checking something that is true no matter what.

One session, both artifacts, one loose prompt. The test and the implementation come from the same interpretation of the same vague instruction, so they agree perfectly and the agreement carries no information. If you delegate the test, the requirement has to be the input, and you have to read the resulting test against the requirement before you trust it as a specification.

Asserting mechanics rather than the guarantee. The test checks that a particular helper was called or that an internal structure has a shape. It breaks on harmless refactoring and stays green when the behavior changes, which is the worst combination available. Assert what the contract promises.

Editing the test when it fails. The implementation is written, a case goes red, and the case is adjusted until it passes. Sometimes the test genuinely was wrong, and the way to tell is that you can point at the contract line proving it. If the justification is that the code does something else, the code is the thing that is wrong.

Checklist
[ ] Every test I wrote today came from a contract row or an acceptance criterion, not from a source file

[ ] The implementation did not exist when I wrote the test

[ ] Every comparison in the requirement is covered on both sides and on the boundary

[ ] Every acceptance criterion on the work item has at least one case, including the ones about absence

[ ] I ran each test and saw it fail on its assertion, not on a missing name

[ ] The failure message identified the case by id and showed the values I expected

[ ] The failing test is committed before the implementation that satisfies it

[ ] Where I delegated the implementation, the task named the test and forbade modifying it

[ ] Where a test changed after going red, I can point at the contract line that justified the change

[ ] Nothing I asserted would break if the implementation were refactored without changing behavior