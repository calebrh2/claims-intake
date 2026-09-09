Instructions
1. Wire the HTTP surface. src/claims/api/routes.py. One endpoint accepting a notification. It parses into NotificationRequest, calls submit_notification, and maps the outcome to a response.

The mapping is where your contract earns its keep. An accepted notification returns 201 with the claim reference. A rule failure returns the status section 6 assigns to that rule's code. A parse failure returns 400 in the standard envelope. PolicyLookupFailed returns the 5xx status its reason maps to. Every response uses the one envelope, and no response exists that section 6 does not describe.

2. Write the integration tests. tests/integration/test_routes.py. These exercise the service through HTTP rather than by calling functions. Cover an accepted notification, at least one rejection per rule, a parse failure, and all three dependency reasons. Assert the status, the code, and the presence of the values in detail that make the error actionable.

3. Build the image. A Dockerfile that runs the service. Build it with docker buildx build --platform linux/amd64. Then explain in README.md why that flag is there, in your own words, in a way a new joiner would understand without already knowing the answer.

4. Complete the README. Someone who has never seen this repository follows it and ends up with a running service. Include what the service does, how to run it, how to run the tests, and the platform note from step 3. Assume they are inside the container and do not tell them to install anything.

5. One bounded task in Cursor. Choose a single self-contained piece of this lab, do it in Cursor rather than in your usual agent, and write a short comparison in docs/tool-comparison.md. The comparison is what is graded, not the code. Say what each tool made easy, what it made awkward, and on what kind of task you would reach for one over the other. An answer that says both are good is not an answer.

6. Open the pull request. Description carries what, why, what to look hardest at, and how it was verified. Your pipeline is green before you request review.

7. Review your partner's pull request. Read in risk order with the contract open. Check the rule table row by row. Check for what is absent as well as what is present. Label every comment as blocking, a question, or a suggestion. Where you block on correctness, cite the contract section rather than your opinion.

8. Respond to the review on your own change. Every blocking comment is either resolved or answered with a reason. Answering is legitimate. Ignoring is not.

9. Merge. After the review is resolved and the required checks pass.
