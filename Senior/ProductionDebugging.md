[English](./ProductionDebugging.md) | [Tiếng Việt](./ProductionDebugging.vi.md)

[← Senior Topics](./README.md)

# Debugging Production Issues

## Process

```text
1. Observe — crash logs, error rates, user reports
2. Reproduce — can you reproduce locally or in a staging environment?
3. Isolate — which build, OS version, device type, user segment?
4. Fix — targeted change with minimal blast radius
5. Verify — deploy, monitor metrics, confirm resolution
```

## Tools

- **Firebase Crashlytics / Sentry** — crash symbolication and grouping
- **dSYM files** — required for symbolicated crash logs; archive and upload on every release
- **MetricKit** — on-device performance and crash data
- **TestFlight** — distribute debug builds to reproduce issues

## Common Production-Only Issues

- Race conditions that appear under real load
- Memory pressure on older devices
- Localization or timezone edge cases
- API contract changes not caught in development

## Practice Questions

- How do you approach a random production crash?

## Senior Take

A production crash with no reproduction path requires building hypotheses from the data you have: stack trace, OS/device distribution, app version range, user cohort. Narrow the hypothesis space before writing any fix.

## Exercise

Given a Crashlytics report showing a `nil` force-unwrap crash in `CartViewController.viewDidLoad` affecting only iOS 16 users on version 2.3.1: write out your full debugging process — what hypotheses you form, what data you gather next, and what the fix strategy looks like before you've reproduced it locally.
