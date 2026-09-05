[English](./FeatureFlagsExperimentation.md) | [Tiếng Việt](./FeatureFlagsExperimentation.vi.md)

[← Senior-Level Topics](./README.md)

# Feature Flags and Experimentation

## Key Idea

A feature flag is a runtime branch that outlives the PR that added it unless someone deliberately removes it. Treating flags as free is how a codebase accumulates permanent, tangled conditional logic that nobody can safely delete.

## What To Review

- Flag categories — release flags (temporary, gate an in-progress feature), ops/kill-switch flags (permanent, disable a risky feature under load or incident), permission flags (entitlement-based), experiment flags (A/B test variant assignment)
- Remote config vs local build flags — a remote-configurable flag can change behavior without a new App Store submission, at the cost of needing offline/cache-miss default behavior defined
- A/B test mechanics — variant assignment (usually a stable hash of user ID, not random per session), sample ratio mismatch as a signal the randomization is broken, guardrail metrics that can auto-abort an experiment
- Statistical validity basics — why peeking at results early and stopping as soon as they look significant inflates false positives, and why sample size must be decided before starting
- Flag lifecycle and cleanup — every release flag needs an owner and a removal date; a flag left in code after full rollout is dead weight and a source of "why does this branch even exist" bugs
- Testing under flags — a flag combinatorially multiplies app states; deciding which combinations are actually worth testing (usually: default state, each flag flipped alone, not the full cross-product)
- Client-side risk — a flag SDK outage or slow fetch must have a safe default; a feature that fails open (enabled) when it should fail closed (disabled) is a common production incident
- Flag-driven UI consistency — a user shouldn't see a feature flicker on mid-session because a flag re-fetched; flag state is typically snapshotted per app session/launch

## Example

```swift
enum PaywallVariant { case control, redesign }

func paywallVariant(for userId: String) -> PaywallVariant {
    // Stable hash-based bucketing — same user always lands in the same variant
    let bucket = stableHash(userId) % 100
    return bucket < 50 ? .control : .redesign
}
```

## Practice Questions

- Why is random-per-session variant assignment usually wrong for an A/B test?
- What should happen if the flag-fetch network call fails on cold launch?
- Why does a "temporary" release flag from six months ago count as tech debt?

## Senior Take

The interview signal here is whether someone has actually owned the mess a flag system creates over time, not just used one. A strong answer names a concrete failure mode: an experiment that shipped a false positive because someone stopped it early, a kill-switch that failed open during an incident because the default wasn't set defensively, or a codebase with a dozen release flags nobody remembers the purpose of. The fix in each case is process (flag ownership, removal dates, guardrail metrics), not just "we use LaunchDarkly."

## Exercise

Design the flag and experimentation setup for testing a new onboarding flow against the current one. Specify: the flag category and how variant assignment is bucketed, what happens on first launch if the remote config fetch hasn't completed yet, one guardrail metric that would auto-abort the experiment, and your plan (owner, deadline, condition) for removing the flag once a winner is decided.
