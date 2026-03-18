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

## Exercise

Review a PR that introduces a new `UserProfileViewModel` with a `URLSession.shared` call inside `init`. Write three comments: one `[blocking]` for the architectural issue, one `[suggestion]` for naming, and one acknowledgement of something done well. Then explain how you would handle pushback from the author who disagrees with the blocking comment.
