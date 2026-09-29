[English](./CodeReview.md) | [Tiếng Việt](./CodeReview.vi.md)

[← Senior Topics](./README.md)

# Code Review Mindset

## What To Look For

- **Correctness** — does it do what is intended? Edge cases covered?
- **Readability** — can the next engineer understand it without explanation?
- **Safety** — memory, threading, error handling, force unwraps
- **Testability** — is the new code testable? Does it break existing tests?
- **Architecture fit** — does it follow established patterns, or introduce new ones without reason?

## How to Give Feedback

- Be specific — point to the exact line and explain why
- Separate blocking issues from suggestions — label `[nit]`, `[suggestion]`, `[blocking]`
- Ask questions before assuming — "What was the intent here?" opens dialogue
- Acknowledge good code — not just problems

## Practice Questions

- How do you review a large PR?
- How do you handle disagreement over an approach?

## Senior Take

A code review is a teaching moment and a quality gate — not a gatekeeping exercise. The goal is a better codebase and a stronger team, not proving the reviewer is smarter.

## Practice Question Answers

### How do you review a large PR?

First I ask whether the PR really needs to be this big; if possible, I suggest splitting it into several smaller PRs by logical step, because review quality drops sharply once a PR reaches thousands of lines.

If it cannot be split (for example, a migration that is already done), I review in this order:

1. Read the PR description, ticket, and design doc to understand the intent and scope.
2. Look at the overall structure first: which files are new, which public APIs or protocols changed, which dependencies were added.
3. Go deep on high-risk areas: concurrency, persistence and migrations, payments, code that runs at app launch, API contract changes.
4. Check the tests: are there tests for the new behavior and edge cases?
5. Leave renames, formatting, and mechanical refactors for last and skim them.

For a very large PR, I often ask the author for a 15-minute walkthrough, or review commit by commit if the commits are cleanly separated. Comments are labeled `[blocking]`, `[suggestion]`, `[nit]` so the author knows what must be fixed.

Trade-off: asking for a split also costs the author time. If the deadline is tight, it can be acceptable to review with a focus on risky areas and create follow-up tickets for the rest. What you should not do is "LGTM" a huge PR without actually reading it.

### How do you handle disagreement over an approach?

I split disagreements into two kinds: issues with objective criteria (correctness, crashes, security, violating conventions the team agreed on) stay `[blocking]`; issues of taste are the author's call.

Concretely:

- **Ask about intent first:** "What was the reason for this approach?" — the author often has context the reviewer does not.
- **Talk in consequences, not feelings.** For example, with `UserProfileViewModel` calling `URLSession.shared` in `init`: "Because the network call runs in init, the view model can't be tested with a mock, and every time the view is recreated it may fire another request."
- **Offer an alternative:** inject a `ProfileService` protocol through init and trigger loading in `.task`.
- **Switch channels when needed:** after 2–3 rounds of comments without agreement, move to a direct conversation or a short call; long threads easily turn into arguments.
- **Bring in a third party if stuck:** the tech lead, the module owner, or the team's guidelines; if a new convention comes out of it, write it down so the debate doesn't repeat.

Trade-off: not every disagreement is worth blocking a PR. If the author's approach is acceptable and easy to change later, I approve with a suggestion — keeping team speed and trust matters more than winning an argument.

## Interview Traps

### "How many comments do you usually leave? What kind of issues do you catch?"

**Common wrong answer:** Being proud of very thorough reviews with dozens of comments about whitespace, import order, and brace placement. It shows you spend human time on work a machine can do.

**Better answer:** Style and formatting should be automated with SwiftLint or SwiftFormat on CI so nobody has to comment on them. Reviewers focus on correctness, design, risk, and maintainability. The number of comments is not a measure of review quality; one well-placed `[blocking]` comment is worth more than 30 nits.

### "CI is green and all tests pass. Do you still need to read it carefully?"

**Common wrong answer:** "If CI passes, that's enough; I just skim." Passing tests only prove the existing tests pass, not that the code is correct.

**Better answer:** CI does not catch design flaws, race conditions, untested edge cases, changes that affect the privacy manifest or data collection, or missing data migrations. A reviewer should also ask "which tests are missing?", not only "do the tests pass?". CI is the basic safety net; review is where you catch what machines don't understand.

### Finding a major architectural problem in a PR that is almost done

**Common wrong answer:** Blocking the PR and demanding a full rewrite, or the opposite — silently approving to avoid conflict.

**Better answer:** Assess impact first: if the problem causes bugs or locks in a direction that is hard to reverse, block it and work with the author on the smallest fix; if it is merely suboptimal, merge with a follow-up ticket. More importantly, fix the root cause: large tasks need a design review or an early draft PR, so architectural disagreements surface before thousands of lines are written.

## Exercise

Review a PR that introduces a new `UserProfileViewModel` with a `URLSession.shared` call inside `init`. Write three comments: one `[blocking]` for the architectural issue, one `[suggestion]` for naming, and one acknowledgement of something done well. Then explain how you would handle pushback from the author who disagrees with the blocking comment.
