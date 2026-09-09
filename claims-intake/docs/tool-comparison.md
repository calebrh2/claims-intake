## Task in scope

The bounded task this comparison is about (pick one and keep it specific):

**Your task (one sentence):**

> The task I am talking about is creating work trees. 

## What Cursor made easy

> Cursor made making changes to the work tree and applying them to the source branch and pushing very easy.

## What Cursor made awkward


> Cursor made creating the actual work tree awkward. I had to create an actual branch first and then attach the work tree to that branch. The /worktree command in cursor doesn't work with a non-existing branch. It was also awkward finding the actual worktree in my directory. It was under a hidden folder and an obscure name (/root/.cursor/worktrees/test-worktree-ab494190/claims-intake-95bb3c064bd8).

## Preference

State which kind of work you would take to Cursor and which kind you would
take to another tool (your usual agent, the editor, tests first by hand),
and **why**. Name the kind of task. "I would use both" does not meet the
criterion.

**Your preference and reason:**

> Overall, Cursor has done a ton of help throughout the entire project process. I created a skill that spins up grading subagents and implements assignment material, and it has worked very well based on my initial review. You can't just copy and paste the project into cursor and expect it to one-shot it without any skills/subagents, but with my workflow it works very well. For example, initially in assignment 2 (build the boundary), Cursor hallucinated the name of a class that was not part of the original assignment.
I trust Cursor to implement the actual application logic, especially since it is running unit/integration tests and doing subagent grading in a loop. That being said, the code requires a human eye to look at it and you do need to add extensive context+ explicit instructions before doing anything. This also applies to unit/integration testing.