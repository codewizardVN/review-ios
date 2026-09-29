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
- **MetricKit** — the app receives metric reports (launch time, hangs, memory, how often the system terminated it) and diagnostics (crashes, hangs, CPU exceptions) from users' devices, usually delivered daily
- **Xcode Organizer** — crashes, hangs, energy, and other metrics Apple collects from users who agreed to share data, with no third-party SDK needed
- **TestFlight** — distribute builds with extra logging or diagnostics to a tester group to reproduce issues. Note that TestFlight builds are distribution-signed and usually built with the Archive configuration (Release by default) like the App Store version, so you can't attach a debugger

## Common Production-Only Issues

- Race conditions that appear under real load
- Memory pressure on older devices
- Localization or timezone edge cases
- API contract changes not caught in development

## Practice Questions

- How do you approach a random production crash?

## Senior Take

A production crash with no reproduction path requires building hypotheses from the data you have: stack trace, OS/device distribution, app version range, user cohort. Narrow the hypothesis space before writing any fix.

## Practice Question Answers

### How do you approach a random production crash?

I don't start by changing code; I start by using data to turn a "random" crash into a pattern with clear conditions, and only then form hypotheses and fix.

Steps:

1. **Assess severity:** how many users are affected, how much the crash-free rate dropped, which version it started in. This decides whether it needs an urgent hotfix or can go into a regular release.
2. **Read the symbolicated stack trace** (make sure the dSYM for that exact build was uploaded): what type of exception — `EXC_BREAKPOINT` is usually a Swift runtime trap such as force-unwrapping `nil` or an index out of range, `EXC_BAD_ACCESS` is an invalid memory access, `0x8badf00d` is a watchdog kill because the main thread was blocked too long. Did it crash on the main thread or a background thread?
3. **Find what's common:** OS version, device, app version, locale, app state (just opened from a push, from background, low memory). Breadcrumbs and logs before the crash are very valuable.
4. **Form and test hypotheses:** for example, a crash only on iOS 16 in `CartViewController.viewDidLoad` suggests an API or lifecycle behavior difference on iOS 16, or data (from a deep link, from cache) that isn't ready yet. Try to reproduce on a real device running iOS 16 or an iOS 16 simulator (if your current Xcode can still install that runtime), with Thread Sanitizer enabled, and with a slow network simulated via Network Link Conditioner.
5. **If you still can't reproduce it:** ship a defensive fix (remove the force unwrap, handle `nil` safely) together with logging or a non-fatal event to confirm the hypothesis, and use a feature flag if the failing area can be turned off.
6. **Verify with data:** crashes drop in the new version.

Trade-off: a defensive fix like `guard let` can hide the real bug. Always add logging so you still know how often the abnormal state happens and why.

## Interview Traps

### "The crash log is all hex addresses, no function names. What do you do?"

**Common wrong answer:** "Download the dSYMs from App Store Connect because Apple recompiles the bitcode." This knowledge is outdated.

**Better answer:** Bitcode was deprecated in Xcode 14 and the App Store no longer accepts bitcode, so Apple no longer recompiles the app; the dSYM is produced at archive time and must be uploaded from that same build (usually automated in CI, for example Crashlytics' upload-symbols script). If it was missed, you can still take the dSYM from the saved `.xcarchive` (Xcode Organizer → Show Package Contents → `dSYMs`) and upload it again. Check that the dSYM's UUID matches the binary with `dwarfdump --uuid`. If the dSYM for a shipped build is lost, that build's crashes can hardly be fully symbolicated, so this must be automated from the start.

### "You tried a debug build on your device, no crash — so it's fine?"

**Common wrong answer:** "If it doesn't reproduce in debug, it's probably rare; let's park it." Debug builds differ from Release builds in important ways.

**Better answer:** Release builds are optimized, have different timing, and run without a debugger attached. Some bugs only show up with optimization and real timing, such as race conditions; the watchdog also doesn't kill the app while a debugger is attached. Try with the Release configuration or a TestFlight build, on an older device, with network and memory conditions similar to real users.

### "The top frame in the stack trace is where the bug is, right?"

**Common wrong answer:** "Yes, fix it where it crashed." The top frame is often just where the error was detected.

**Better answer:** The top frame is often inside a system framework or the runtime, for example a crash in `objc_msgSend` because an object was already deallocated — the real bug is wherever that object's lifetime is managed. Look at the other threads, breadcrumbs, and the "last exception backtrace" if present. Also remember that an app killed by the system for running out of memory (jetsam) usually doesn't produce a normal crash report; that kind of data has to come from MetricKit (`MXAppExitMetric` counts terminations for exceeding the memory limit), Xcode Organizer, or the OOM metrics your crash reporter infers.

## Exercise

Given a Crashlytics report showing a `nil` force-unwrap crash in `CartViewController.viewDidLoad` affecting only iOS 16 users on version 2.3.1: write out your full debugging process — what hypotheses you form, what data you gather next, and what the fix strategy looks like before you've reproduced it locally.
