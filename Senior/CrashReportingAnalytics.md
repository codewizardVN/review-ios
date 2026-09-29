[English](./CrashReportingAnalytics.md) | [Tiếng Việt](./CrashReportingAnalytics.vi.md)

[← Senior-Level Topics](./README.md)

# Crash Reporting and Analytics

## Key Idea

A crash reporting/analytics SDK is production infrastructure, not a library import. The senior-level questions are about symbolication correctness, event schema discipline, and privacy — not which vendor dashboard looks nicer.

## What To Review

- Symbolication pipeline — dSYM upload (manual or via build-phase script), matching dSYM UUID to the exact build that crashed; a mismatched or missing dSYM turns a crash report into unreadable memory addresses
- Crash-free rate as a release gate — tracking crash-free users/sessions percentage per version, and what threshold blocks a rollout from proceeding
- Symbolicating locally vs server-side — Xcode Organizer (or `atos`/`symbolicatecrash` on a dev machine) can only symbolicate when that machine has the exact dSYM, and Organizer only receives crashes from users who agreed to share data with developers; with many versions and several people investigating, that doesn't scale. Server-side crash reporting (Crashlytics, Sentry…) symbolicates every report automatically, provided the dSYM was uploaded — which is why the CI pipeline should upload dSYMs automatically on every archive
- Breadcrumbs and non-fatal logging — recording a trail of recent user actions/state before a crash or handled error, so a report has context beyond the stack trace
- Event schema discipline — versioned event names and typed payloads, avoiding free-text properties that fragment analytics ("purchase_completed" vs "PurchaseComplete" vs "purchase-done" all meaning the same thing)
- Sampling and cost — high-volume events (e.g., scroll position) usually need sampling or client-side aggregation; sending every raw event is often a cost and privacy liability, not a benefit
- Privacy boundaries — what can't go into an event payload (PII, precise location, free-text user content) and how that constrains schema design, tied to what the privacy manifest and nutrition label declare
- Alerting thresholds — a spike detector on crash rate or a key funnel metric, tuned to avoid both alert fatigue and missing a real regression

## Example

```swift
// Bad: free-text, unversioned, no context
Analytics.log("bought item")

// Better: typed, carries context for a "why" without PII.
// (Event names and schema version are defined centrally in the event enum; the Analytics layer adds them to the payload.)
Analytics.log(event: .purchaseCompleted(
    sku: "premium_monthly",
    priceTierCents: 999,
    source: .paywallVariantB
))
```

## Practice Questions

- Why does a missing dSYM matter more than a missing line of code comment?
- Why is "crash-free users" usually a better release gate than raw crash count?
- Why should analytics event names be reviewed like an API, not added ad hoc per feature?

## Senior Take

This is where "we have Crashlytics installed" and "we can actually act on production signal" diverge. The strong answer describes an incident where symbolication or event schema debt actively slowed down debugging — an unreadable crash report, a metric nobody trusted because three teams logged the same event differently — and what process (schema review, automated dSYM upload in CI, a release gate tied to crash-free rate) fixed it structurally instead of one-off.

## Practice Question Answers

### Why does a missing dSYM matter more than a missing line of code comment?

Because without the dSYM a production crash report is just a list of memory addresses, and it's often the only data you have about a bug that can't be reproduced on a dev machine.

Release builds strip symbols out of the binary to make it smaller and harder to reverse-engineer. Function names, file names and line numbers live in a separate dSYM file. When the app crashes, the device only records addresses like `0x1004a3f2c`; the crash reporting server uses the dSYM to translate that into `CheckoutViewModel.submit() CheckoutViewModel.swift:88`.

The key point is that the dSYM must match the UUID of the exact build that crashed. Rebuilding the same commit usually doesn't reproduce that exact binary (a different toolchain, paths, settings… give a different UUID), so don't count on rebuilding. If you don't keep the dSYM from the archive you uploaded to the App Store, that version's crashes become unreadable forever, even though you have all the source.

A missing comment is different: it hurts code readers, but it can be added at any time and loses no production data.

The right approach is for CI to upload dSYMs automatically right after every archive, and to keep the `.xcarchive` for every shipped build. Trade-off: dSYMs expose code structure, so upload them only to services you trust and control access.

### Why is "crash-free users" usually a better release gate than raw crash count?

Because crash-free users is a rate normalized by how many people use that version, so it's comparable across versions, while raw crash count rises and falls with user count, not quality.

In a phased release, about 1% of users with automatic updates get the new version on day one and 100% by day seven. The new version's raw crash count will certainly climb just because more people use it, even if the code isn't worse. Conversely, 50 crashes might be 50 different users or one user in a crash loop 50 times. "99.6% of users had no crash" answers the release gate's actual question: how many people is this version hurting?

A practical gate: halt the rollout if crash-free users drops more than a threshold below the previous version, e.g. 0.3 percentage points, once a minimum session count makes the result meaningful.

Trade-offs:

- Crash-free users hides frequency: a crash-looping user counts once. Track crash-free sessions too.
- With a third-party crash SDK it usually excludes hangs, out-of-memory kills and watchdog kills (see the interview trap below); you need MetricKit or the Xcode Organizer to see those.
- For small apps the rate is noisy; require a minimum sample.

### Why should analytics event names be reviewed like an API, not added ad hoc per feature?

Because an event is a data contract with many consumers, and once shipped you can't fix the old app versions that keep sending it.

An event like `purchase_completed` feeds product dashboards, revenue reports, prediction models and experiments. If every feature names its own, you end up with `purchase_completed`, `PurchaseComplete`, `purchase-done`, and nobody knows which number is right. Like an API, events have these properties:

- Hard to change: old app versions keep running on users' devices for months, still sending the old name. Renaming means mapping both forever.
- Typed: `priceTierCents: Int` versus `price: "9.99$"` decides whether you can sum it.
- Privacy-constrained: a free-text property can accidentally contain a user's email or address.

How to do it: define events as a typed enum like the example's `.purchaseCompleted(sku:priceTierCents:source:)`, keep one shared tracking plan, and review new events in PRs like API changes.

Trade-off: the review process slows down adding exploratory events. You can allow a `debug_` or `exp_` namespace with a short lifetime that's never used for official reporting.

## Interview Traps

### "If we lose a dSYM, can we just download it from App Store Connect?"

**Common wrong answer:** Yes, Apple rebuilds from bitcode, so there's always a dSYM to download in App Store Connect.

**Better answer:** That knowledge is outdated. The "Download dSYM" button in App Store Connect only mattered for bitcode apps, because Apple recompiled them and produced new dSYMs. Bitcode was deprecated in Xcode 14 (the App Store no longer accepts bitcode builds) and the App Store no longer recompiles apps, so the only dSYM is the one Xcode produced when you archived. If you didn't keep the archive or upload the dSYM then, you can't get it back. CI should upload dSYMs right after the archive step and keep the `.xcarchive` for every shipped build.

### "Does the crash reporting SDK catch every time the app dies unexpectedly?"

**Common wrong answer:** Yes, Crashlytics or Sentry install signal handlers, so every death produces a report.

**Better answer:** Signal handlers only run if the process still gets a chance to execute code. When the system kills the app for memory (jetsam, an uncatchable SIGKILL) or the watchdog kills it for blocking the main thread too long at launch or during a state transition (code `0x8badf00d`), the app never gets to write a report; the SDK can at best infer it on the next launch (e.g. Sentry's "watchdog termination" feature deduces that the app died in the foreground last time without a crash). MetricKit fills this gap: `MXCrashDiagnostic` (with the call stack and termination reason), `MXHangDiagnostic` for hangs, and `MXAppExitMetric`, which counts terminations by reason (memory limit, watchdog, crash…). Since iOS 15, diagnostic payloads (crashes, hangs…) are delivered immediately — for a crash that means on the next app launch — instead of in the 24-hour payload as on iOS 14; metric payloads are still delivered daily.

### "If we hash the email before sending it to analytics, it's no longer PII, right?"

**Common wrong answer:** Right, a SHA-256 hash is anonymized, so it can be sent freely and doesn't need to be declared in the nutrition label.

**Better answer:** A hashed email is still a stable identifier: anyone with the same email computes the same hash and can link data across systems. It's identifying data that must be declared in the nutrition label, and if it's used to link with other companies' data for advertising, that's tracking and requires ATT permission. The safe approach is not to send user identifiers in events unless truly needed, and to use a random internal ID if you must join sessions.

## Exercise

Design the crash-reporting and analytics rollout for a new checkout flow. Specify: what non-fatal events you'd log and their schema (with privacy constraints in mind), how dSYMs get uploaded automatically in your CI/CD pipeline, what crash-free-rate threshold would halt a phased rollout, and one debugging scenario where a missing breadcrumb would leave you unable to diagnose a production-only bug.
