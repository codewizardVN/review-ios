[English](./Refactoring.md) | [Tiếng Việt](./Refactoring.vi.md)

[← Senior Topics](./README.md)

# Refactoring Strategy

## When to Refactor

- Before adding a feature to an area that will become harder to change
- When the same bug keeps appearing in the same module
- When onboarding new engineers consistently requires explaining the same confusing area
- When test coverage is zero and the code needs to be changed

## When NOT to Refactor

- Right before a release deadline
- When the code works and is not being touched
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

## Exercise

Pick a `MassiveViewController` in a project (or create a fictional one with 400+ lines). Write characterization tests for its three most important behaviors. Then extract one responsibility into a new class using the Strangler Fig pattern. Verify all tests still pass after the extraction.
