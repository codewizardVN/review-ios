[English](./Refactoring.md) | [Tiếng Việt](./Refactoring.vi.md)

[← Senior Topics](./README.md)

# Refactoring Strategy

## When to Refactor

- Before adding a feature to an area that will become harder to change
- When the same bug keeps appearing in the same module
- When onboarding new engineers consistently requires explaining the same confusing area
- When an area has no tests at all but is about to be changed — a small refactor to create seams (inject dependencies) and add characterization tests is the preparation step, not a big refactor

## When NOT to Refactor

- Right before a release deadline
- When the code works and nothing is planned for that area — refactoring it now only adds risk without any benefit
- As a prerequisite to all other work ("we can't add features until we refactor everything")

## Approaches

- **Strangler Fig** — build the new system alongside the old, gradually migrate traffic, remove old code when done
- **Extract and redirect** — extract logic into a new module/class, redirect callers one by one
- **Characterization tests** — write tests to capture current behavior before changing it

## Practice Questions

- When to refactor and when to leave the code as-is?
- How do you refactor a legacy codebase without breaking existing behavior?

## Senior Take

Refactoring without tests is dangerous. The first step is almost always: add tests to the existing behavior, then change it. Characterization tests capture current behavior — even bugs — so you know when something changed.

## Practice Question Answers

### When to refactor and when to leave the code as-is?

I refactor when bad code is getting in the way of work that is about to happen, and I leave it alone when it is ugly but stable and nobody needs to touch it.

"Ugly" code on its own is not a reason. The reason is real cost: the same bug keeps coming back in one module, every new feature in that area takes twice as long, or every new engineer asks about the same confusing spot.

Refactor when:

- You are about to add a feature to that area — refactor just enough that the new feature fits cleanly ("make the change easy, then make the easy change").
- Bugs keep coming from the structure, for example the same state stored in two places that drift apart.

Leave it alone when:

- The code works, rarely changes, and rarely breaks — refactoring now only adds risk.
- You are right before a release deadline.
- There are no tests and no time to write characterization tests.

I also avoid proposing "stop features for two months to refactor everything" — product will struggle to agree and the risk is very high. It is better to refactor step by step alongside feature work, and present the benefit to stakeholders in numbers (bug counts, feature lead time).

Trade-off: if you keep postponing, technical debt piles up. Have a fixed budget, for example 10–20% of each sprint's capacity, for the most painful areas.

### How do you refactor a legacy codebase without breaking existing behavior?

The safe way is to lock down current behavior with tests first, then change things in small steps, each of which can be shipped and rolled back.

The process I use, taking `MassiveViewController` as the example:

1. **Characterization tests** for the most important behaviors — computing a total, validating a form, handling network errors. The tests record what the code does today, including slightly wrong behavior, so you know immediately when something changes.
2. **Create seams:** pass dependencies like `URLSession`, `UserDefaults`, and singletons in through init or a protocol, so the code becomes testable without changing logic yet.
3. **Extract and redirect:** pull one responsibility (for example validation) into a new class, move callers over one by one, and run the tests after each step.
4. **Strangler Fig** for larger changes: build the new implementation alongside the old one, enable it via a feature flag for a portion of users, compare metrics, then delete the old code.
5. **Never mix refactoring with behavior changes in one PR**, so review is easy and any regression has an obvious cause.

Trade-off: characterization tests for old UIKit code can be hard to write and slow to run. In that case, prioritize tests at the logic layer right after extracting it, plus a few UI or snapshot tests for the main flows. Don't try to reach high coverage across the whole codebase before starting — you only need enough for the area you are about to touch.

## Interview Traps

### "This code is terrible — why not rewrite it from scratch?"

**Common wrong answer:** "I'd rewrite the whole thing in SwiftUI with a clean new architecture." It sounds decisive but is a red flag about judgment.

**Better answer:** Big-bang rewrites rarely succeed: you lose years of bug fixes and edge cases implicitly encoded in the old code, feature work stops for a long time, and two codebases coexist meanwhile. I prefer an incremental approach with Strangler Fig, moving one screen or flow at a time. A rewrite only makes sense when the scope is small, there is a concrete reason (such as an unsupported technology), and there is a clear cut-over plan.

### "Can you add the feature in the same PR while you're refactoring?"

**Common wrong answer:** "Sure, the file is already open, so it's faster." When a regression appears, nobody knows whether it came from the refactor or the feature.

**Better answer:** Keep them separate. A refactoring PR must not change behavior, and the existing tests must stay green without being modified (except tests tightly coupled to internal structure). The feature PR comes next, on top of the cleaned-up code. This makes review faster, and if something must be reverted you can revert exactly the broken part.

### "You find a bug while refactoring. Do you fix it right away?"

**Common wrong answer:** "Yes, I'm already in there." It sounds reasonable but turns a refactoring PR into a behavior-changing PR.

**Better answer:** Note the bug, let the characterization tests keep reflecting current behavior, and fix it in a separate PR with a clear description. Other parts of the app, the backend, or users themselves may depend on that behavior (Hyrum's law). Fixing it separately lets you assess impact, test it properly, and roll it back if needed.

## Exercise

Pick a `MassiveViewController` in a project (or create a fictional one with 400+ lines). Write characterization tests for its three most important behaviors. Then extract one responsibility into a new class using extract and redirect (move callers to the new class one by one); if you want to practice Strangler Fig, keep the old and new paths side by side behind a flag before deleting the old one. Verify all tests still pass after the extraction.
