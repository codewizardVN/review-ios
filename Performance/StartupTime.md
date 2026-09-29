[English](./StartupTime.md) | [Tiếng Việt](./StartupTime.vi.md)

[← Performance](./README.md)

# Startup Time

## Two Phases

1. **Pre-main** — everything that happens before `main()` runs: the kernel creates the process, dyld loads and links dynamic libraries/frameworks, the Objective-C runtime registers classes/categories and runs `+load` methods, and C/C++ static initializers run (`__attribute__((constructor))`, constructors of C++ globals)
2. **Post-main** — from `main()` / `UIApplicationMain` until the first frame is shown: UIKit/SwiftUI initialization, `application(_:didFinishLaunchingWithOptions:)`, scene and initial view hierarchy creation, rendering the first frame

## What Slows Startup

- Too many dynamic frameworks (each adds work for dyld: mapping the file, verifying its signature, fixing up pointers)
- Heavy code in `+load` or C/C++ static initializers (runs in pre-main). Note: Swift `static let` and globals are initialized lazily on first access, not in pre-main — but if you touch them in `didFinishLaunching`, the cost still counts toward post-main
- Synchronous network or disk access at launch
- Complex initial view setup before first frame

## How to Measure

- Instruments → App Launch template: splits launch into phases (process creation, dyld, static initializers, UIKit init, initial frame rendering) and shows which code runs in each phase
- Xcode Organizer → Metrics → Launch Time: launch data from real users' devices (per app version, by percentile)
- MetricKit `MXAppLaunchMetric`: time-to-first-draw and resume-time histograms, collected in-app in production
- `XCTApplicationLaunchMetric` in performance tests to measure automatically and catch regressions
- (`DYLD_PRINT_STATISTICS=1` is the old dyld2-era approach; on modern iOS with dyld3/dyld4 it no longer gives useful output)

## Improvements

- Reduce dynamic framework count (merge small modules, link statically, or use mergeable libraries from Xcode 15)
- Move expensive setup after the first frame, and run it in the background if it doesn't need the main thread
- Defer non-critical initialization (`lazy var`, initialize on first real use)
- Understand prewarming (iOS 15+): it's not a feature you turn on but system behaviour — the system may run your app's pre-main part before the user opens it so the next launch is faster. Your code must tolerate that (see Interview Traps)

## Practice Questions

- After measuring pre-main time and identifying the three most expensive post-main operations with Instruments' App Launch template, what concrete change would you propose for each?

## Senior Take

A 400ms improvement in launch time is real user value. But measure before optimizing — pre-main and post-main have different root causes and different fixes. Instrument first.

## Practice Question Answers

### After measuring pre-main time and identifying the three most expensive post-main operations with Instruments' App Launch template, what concrete change would you propose for each?

The general rule: anything not needed for the first frame is moved after the first frame, done in the background, or made lazy until actually needed. A note on measurement: older material measured pre-main with `DYLD_PRINT_STATISTICS=1`, but on modern iOS (dyld3, then dyld4) this variable prints almost nothing useful for apps. So take pre-main numbers from the App Launch template itself — it splits launch into phases such as process creation, dyld, static initializers, UIKit init and initial frame rendering; pre-main is the phases before UIKit init.

Three common expensive post-main operations and how to fix them:

- **SDK initialization in `didFinishLaunching`** (analytics, ads, remote config, A/B testing): keep only the crash reporter synchronous; initialize the other SDKs after the first screen appears, at low priority. Careful: in `didFinishLaunching` (which runs on `@MainActor`), `Task(priority: .utility) { ... }` still inherits the main actor, so synchronous code inside it still runs on main; if the SDK allows initialization off main use `Task.detached(priority: .utility)` or a `@concurrent` function, and if the SDK requires the main thread, just defer it past the first frame.
- **Synchronous disk/database work:** loading the Core Data store, running migrations, reading large JSON/plist files, reading the Keychain. Make it async, show a skeleton UI while waiting, and run heavy migrations in the background.
- **An overly heavy initial view hierarchy:** a root tab bar that builds all 5 tabs up front, large storyboards, loading fonts or large images. Build only the visible tab, make the other tabs lazy, simplify the first screen.

If pre-main is large: reduce the number of dynamic frameworks (link statically, or use mergeable libraries from Xcode 15), and remove heavy code in `+load` and static initializers.

After each change, measure again under the same conditions (cold launch, real device, release build), which you can automate with `XCTApplicationLaunchMetric` in a performance test; after release, confirm with Launch Time in Xcode Organizer or MetricKit's `MXAppLaunchMetric`. Trade-off: deferring work past the first frame can simply move the delay to the next screen, so also check the experience right after launch.

## Interview Traps

### "How do you measure pre-main?"

**Common wrong answer:** Set `DYLD_PRINT_STATISTICS=1` in the scheme and read the console log.

**Better answer:** That's outdated knowledge: since dyld3 (used for apps from iOS 13) and then dyld4 (newer iOS versions) replaced dyld2, this environment variable has essentially no effect for iOS apps. The current approach is the App Launch template in Instruments (with separate dyld and static-initializer phases), Launch Time in Xcode Organizer for real-user data, and MetricKit's `MXAppLaunchMetric`.

### "Running from Xcode, launch takes 2 seconds, so the app launches slowly?"

**Common wrong answer:** Pressing Run in Xcode with a debug build is a reliable way to measure launch.

**Better answer:** An attached debugger and a debug build (unoptimized, with extra diagnostics) make launch much slower than reality. You must distinguish cold launch (after a reboot or a long time unused, dylibs not in memory) from warm launch (recently opened). Measure on a real device, release build, no debugger attached, averaged over several runs.

### "Prewarming makes launch faster, so static-initializer code definitely runs when the user opens the app?"

**Common wrong answer:** Pre-main always runs right before the user sees the app, so you can rely on it to measure time or prepare the user's data.

**Better answer:** Since iOS 15 the system may prewarm: run the process up to just before `UIApplicationMain` (dyld, static initializers) while the user hasn't opened the app, then suspend it, sometimes for hours. So don't use process start time as your launch baseline (the `ActivePrewarm` environment variable equal to `"1"` tells you it's a prewarm), and don't access data-protected files, the Keychain or user state in initializers — the device may be locked at that moment.

## Exercise

Build for release and profile the app with Instruments' App Launch template on a real device (cold launch: remove the app from memory, ideally reboot before the first measurement). Record the pre-main time (the dyld and static-initializer phases) and the total time to the initial frame, then identify the three most expensive operations in post-main. Propose one concrete change to reduce each. Write a performance test using `XCTApplicationLaunchMetric` to measure before/after, and describe how you would track the result in production (Launch Time in Xcode Organizer, MetricKit's `MXAppLaunchMetric`).
