[English](./FeatureFlagsExperimentation.md) | [Tiếng Việt](./FeatureFlagsExperimentation.vi.md)

[← Senior-Level Topics](./README.md)

# Feature Flags and Experimentation

## Key Idea

A feature flag is a runtime branch that outlives the PR that added it unless someone deliberately removes it. Treating flags as free is how a codebase accumulates permanent, tangled conditional logic that nobody can safely delete.

## What To Review

- Flag categories — release flags (temporary, gate an in-progress feature), ops/kill-switch flags (permanent, disable a risky feature under load or incident), permission flags (entitlement-based), experiment flags (A/B test variant assignment)
- Remote config vs local build flags — a remote-configurable flag can change behavior without a new App Store submission, at the cost of needing offline/cache-miss default behavior defined
- A/B test mechanics — variant assignment (usually a stable hash of user ID, not random per session), sample ratio mismatch (SRM — a 50/50 split that actually yields e.g. 52/48 over a large user base, a gap far beyond chance) as a signal that randomization or exposure logging is broken, so that experiment's results can't be trusted; guardrail metrics (crash rate, revenue, cancellation rate…) that can auto-abort an experiment when a variant is causing harm
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
    // stableHash is a team-written deterministic hash returning UInt64 (never negative) — see the interview trap below
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

## Practice Question Answers

### Why is random-per-session variant assignment usually wrong for an A/B test?

Because the same user will see both control and the new variant in turn, so you can no longer measure each variant's effect on a person, and the user's experience gets scrambled.

An A/B test compares two separate groups of people. If you re-randomize each session:

- Results get contaminated: a purchase in session three may be influenced by the paywall redesign seen in session two, but gets credited to control.
- Observations are no longer independent: a heavy user contributes to both groups, skewing the statistics.
- Per-user metrics (retention, revenue per user) can't be computed because the user doesn't belong to either group.
- Bad UX: prices look one way today and another way tomorrow.

That's why the file's example uses `stableHash(userId) % 100`: the same user always lands in the same bucket. Add the experiment name to the hash input so different experiments don't split users identically:

```swift
let bucket = stableHash("paywall_redesign_v1:" + userId) % 100
```

For logged-out users, use a persisted install ID (e.g. in the Keychain) and accept that switching devices re-buckets them.

Trade-off: per-session randomization only makes sense when the unit of analysis really is the session and the change has no lasting effect, e.g. search result ordering — but then you must analyze per session, not per user.

### What should happen if the flag-fetch network call fails on cold launch?

The app must still open normally with safe values: use the cached values from the last successful fetch, fall back to defaults compiled into the app if there are none — and never block launch waiting on the network.

The usual priority order:

1. Cached values from last time, already "activated" in a previous session.
2. Bundled defaults on first launch or if the cache is corrupt.
3. Fetch in the background with a short timeout; new values apply from the next launch so the UI doesn't flicker mid-session.

The default depends on the flag category. A release flag for an in-progress feature should fail closed (off). A kill switch for a stable feature usually defaults to the feature still running, because being offline isn't an incident. A risky feature (new payments) is always off when in doubt.

For experiments, a user without an assignment gets control and no exposure is logged, so the data isn't contaminated. Log exposure only when the user actually sees the variant.

Trade-off: applying on next launch means a kill switch that must take effect immediately lags by a session. For that kind of flag, allow applying immediately at safe points, e.g. before opening the checkout screen, instead of changing UI that's already on screen.

### Why does a "temporary" release flag from six months ago count as tech debt?

Because it keeps a code branch nobody uses that still has to be read, built, tested and maintained, and it can be flipped the wrong way at any time.

A release flag exists to gate an in-progress feature. Once the feature is at 100%, the `else` branch is dead code, but the costs remain:

- Every flag doubles the number of app states; ten stale flags is 1024 combinations in theory.
- New readers don't know which branch is real and have to ask or guess.
- The old branch is no longer tested; if someone, or a remote config mistake, changes the value, users see the old UI with bugs fixed long ago.
- Refactoring is blocked because both paths must keep working.

The fix is process: every release flag gets an owner and an expiry date at creation; once rollout completes, a removal ticket is opened; CI or lint warns on expired flags.

```swift
@Flag(owner: "checkout-team", expires: "2026-12-01")
var newCheckout = false
```

(`@Flag` here is a team-written property wrapper, not a system API.)

Trade-off: kill switches and permission flags are designed to be long-lived and aren't debt. The problem is only a release flag left behind as if it were a kill switch.

## Interview Traps

### "Can `stableHash` in the example just be `userId.hashValue`?"

**Common wrong answer:** Yes, `hashValue` of the same `String` always gives the same number, so bucketing is stable.

**Better answer:** No. Swift's `Hasher` is randomly seeded on every process launch, so `hashValue` changes each time the app opens — users would jump variants every launch, exactly the random-per-session bug. It also differs between iOS and the server, so the backend can't recompute the bucket. Use a deterministic hash like FNV-1a, or the first few bytes of `SHA256` (CryptoKit), over `experimentKey + userId`.

### "With remote config, can we ship new features without going through App Review?"

**Common wrong answer:** Yes, ship the code behind a flag that's off, then turn it on for users after review.

**Better answer:** Flags should only toggle code that was reviewed. Under guideline 2.3.1, apps must not contain hidden, dormant, or undocumented features; hiding a feature from the reviewer and enabling it later can get the app removed. Guideline 2.5.2 forbids downloading new executable code that changes functionality. The right approach is to enable the feature for the review account or describe it in the review notes; remote config is for gradual rollout, not for dodging review.

### "The experiment was significant on day three — can we stop early and ship?"

**Common wrong answer:** Yes, p below 0.05 means the result is certain; waiting longer just wastes time.

**Better answer:** If you check results every day and stop the first time p < 0.05, the real false-positive rate is far above 5%, because you're giving random noise many chances to cross the threshold. Sample size and duration (usually at least one full weekly cycle) must be decided up front. If you need to stop early, use a method designed for it, such as sequential testing; guardrail metrics, on the other hand, are allowed to abort early when a variant is causing harm.

## Exercise

Design the flag and experimentation setup for testing a new onboarding flow against the current one. Specify: the flag category and how variant assignment is bucketed, what happens on first launch if the remote config fetch hasn't completed yet, one guardrail metric that would auto-abort the experiment, and your plan (owner, deadline, condition) for removing the flag once a winner is decided.
