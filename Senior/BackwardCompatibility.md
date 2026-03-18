[English](./BackwardCompatibility.md) | [Tiếng Việt](./BackwardCompatibility.vi.md)

[← Senior Topics](./README.md)

# Backward Compatibility

## Key Idea

Backward compatibility means new code should not break older clients, persisted data, or supported OS versions without an intentional migration plan.

## What To Review

- API contract changes and fallback behavior
- Database or cache migrations
- Feature flags for staged rollout
- OS availability checks and graceful degradation

## Example

If a server adds a new required field, older app versions may fail unless decoding is tolerant or the backend supports a transition period.

## Practice Questions

- How do you ship a new feature while supporting older app versions?
- When do you need a migration instead of a silent fallback?

## Senior Take

Compatibility work is product work. A strong senior answer considers real users on older builds, staged releases, and recovery paths when assumptions fail in production.

## Exercise

Your team wants to replace a local cache schema and ship a new onboarding step in the same release. Describe the compatibility risks and how you would sequence the rollout safely.
