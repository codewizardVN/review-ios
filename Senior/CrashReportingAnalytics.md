[English](./CrashReportingAnalytics.md) | [Tiếng Việt](./CrashReportingAnalytics.vi.md)

[← Senior-Level Topics](./README.md)

# Crash Reporting and Analytics

## Key Idea

A crash reporting/analytics SDK is production infrastructure, not a library import. The senior-level questions are about symbolication correctness, event schema discipline, and privacy — not which vendor dashboard looks nicer.

## What To Review

- Symbolication pipeline — dSYM upload (manual or via build-phase script), matching dSYM UUID to the exact build that crashed; a mismatched or missing dSYM turns a crash report into unreadable memory addresses
- Crash-free rate as a release gate — tracking crash-free users/sessions percentage per version, and what threshold blocks a rollout from proceeding
- Symbolicating on-device vs server-side — why relying on Xcode's Organizer alone doesn't scale, and why the CI pipeline should upload dSYMs automatically on every archive
- Breadcrumbs and non-fatal logging — recording a trail of recent user actions/state before a crash or handled error, so a report has context beyond the stack trace
- Event schema discipline — versioned event names and typed payloads, avoiding free-text properties that fragment analytics ("purchase_completed" vs "PurchaseComplete" vs "purchase-done" all meaning the same thing)
- Sampling and cost — high-volume events (e.g., scroll position) usually need sampling or client-side aggregation; sending every raw event is often a cost and privacy liability, not a benefit
- Privacy boundaries — what can't go into an event payload (PII, precise location, free-text user content) and how that constrains schema design, tied to what the privacy manifest and nutrition label declare
- Alerting thresholds — a spike detector on crash rate or a key funnel metric, tuned to avoid both alert fatigue and missing a real regression

## Example

```swift
// Bad: free-text, unversioned, no context
Analytics.log("bought item")

// Better: typed, versioned, carries context for a "why" without PII
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

## Exercise

Design the crash-reporting and analytics rollout for a new checkout flow. Specify: what non-fatal events you'd log and their schema (with privacy constraints in mind), how dSYMs get uploaded automatically in your CI/CD pipeline, what crash-free-rate threshold would halt a phased rollout, and one debugging scenario where a missing breadcrumb would leave you unable to diagnose a production-only bug.
