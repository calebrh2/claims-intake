# Rubric

Scored out of 100.

## Service correctness (25 points)

| Level | Points | Descriptor |
| --- | ---: | --- |
| Excellent | 25 | Every rule, every parse failure, and all three dependency reasons produce exactly the response section 6 specifies. The 422 for an absent policy and the 5xx family for a lookup that failed are cleanly distinguished. Errors carry the values the decision was made on. |
| Proficient | 19 | The service is correct across rules and parse failures. One dependency reason is mapped to the wrong 5xx status, or one error omits the detail values that would make it actionable. |
| Developing | 12 | Rules work through HTTP but a structural failure can produce a rule code, or a dependency failure returns a 4xx, so a caller is told to fix a payload that is not wrong. |
| Inadequate | 5 | The happy path works and the failure paths are incomplete or return responses the contract does not describe. |

## Integration testing (15 points)

| Level | Points | Descriptor |
| --- | ---: | --- |
| Excellent | 15 | Coverage spans acceptance, every rule, parse failure, and all three dependency reasons, asserting status, code, and detail contents. Tests exercise the service through HTTP rather than reaching past it, and no test depends on another having run. |
| Proficient | 11 | Coverage is complete against rules and parse failures. One or two dependency reasons are untested, or some tests assert status without asserting the code. |
| Developing | 7 | The main paths are covered and the boundaries are not, or a test passes only because of the order the suite runs in. |
| Inadequate | 2 | Tests demonstrate that valid notifications are accepted and little else. |

## Container and documentation (10 points)

| Level | Points | Descriptor |
| --- | ---: | --- |
| Excellent | 10 | The image builds for the deployment architecture and runs. The README takes a stranger to a running service with no prior knowledge, and the platform explanation shows the author understands why the host and the target differ. |
| Proficient | 8 | The image builds correctly and the README is complete. The platform note restates the command's effect rather than the reason behind it. |
| Developing | 5 | The image builds but without an explicit platform, or the README assumes knowledge the reader does not have. |
| Inadequate | 1 | The image does not build or run, or the README could not be followed by anyone who has not already done this lab. |

## Commit and pull request quality (15 points)

| Level | Points | Descriptor |
| --- | ---: | --- |
| Excellent | 15 | Commits are atomic with specific imperative subjects, and bodies carry decisions and rejected alternatives. The description points the reviewer at the highest risk part of the change rather than summarizing it. Nothing unintended is in the diff. |
| Proficient | 11 | Commits are clean and the description is complete. It summarizes the change without directing the reviewer's attention anywhere in particular. |
| Developing | 7 | Some commits bundle unrelated work, or subjects are generic, or the description leaves the reviewer to reconstruct intent from the diff. |
| Inadequate | 2 | History is a sequence of save points, or the change is large enough that no reviewer could have read it properly and nothing in the description acknowledges that. |

## Peer review (25 points)

| Level | Points | Descriptor |
| --- | ---: | --- |
| Excellent | 25 | The review identifies every correctness defect in the change, including ones the test suite does not catch, and cites the contract section or acceptance criterion that makes each a defect rather than a preference. Comments are labeled, the blocking ones are genuinely blocking, and at least one comment addresses something absent rather than something written. |
| Proficient | 19 | The review identifies the correctness defects and labels comments correctly. Reasoning is sound but at least one blocking comment asserts the problem without citing the authority that establishes it. |
| Developing | 12 | The review finds surface issues such as naming and structure and misses a correctness defect, or leaves comments without indicating which block, so the author cannot tell what stops the merge. |
| Inadequate | 4 | The change was approved without a substantive comment, or the review is a set of preferences with no reference to the contract. An approval is a statement of accountability and this one carries none. |

## Tool comparison (10 points)

| Level | Points | Descriptor |
| --- | ---: | --- |
| Excellent | 10 | The comparison rests on a specific task actually performed, names concrete differences in how each tool handled it, and states which kind of work the author would take to which tool and why. |
| Proficient | 8 | The comparison is grounded in real use and identifies differences, but the preference is stated without a reason that would help someone else choose. |
| Developing | 5 | The comparison describes features of each tool rather than the experience of using them on this task. |
| Inadequate | 1 | The comparison concludes that both are useful, which is a way of not answering the question. |
