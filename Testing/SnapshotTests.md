[English](./SnapshotTests.md) | [Tiếng Việt](./SnapshotTests.vi.md)

[← Testing](./README.md)

# Snapshot Tests

## Key Idea

Snapshot tests render a view and compare it against a stored reference image. They catch unintended visual regressions automatically.

## What To Review

- swift-snapshot-testing (Point-Free) — the most common library; supports both XCTest and Swift Testing, and can snapshot SwiftUI views, `UIView`, `UIViewController` and text-based data too (for example `.dump`, `.json`).
- Recording vs asserting mode: when recording, the library writes a new image as the reference; when asserting, it renders again and compares with the committed image. Since 1.17, the record mode is configured with `withSnapshotTesting(record:)` or the `SNAPSHOT_TESTING_RECORD` environment variable (see the last interview trap).
- Testing on simulator vs device — images differ by device model, iOS version, screen scale and Xcode, so the whole team and CI must record/verify on the same simulator configuration; snapshot tests are usually not run on physical devices.
- What to snapshot: components, not full screens — small components are stable and reused in many places, while full screens change often and must be re-recorded constantly.

## Example

```swift
import SnapshotTesting
import SwiftUI
import XCTest
@testable import MyApp

// ItemRow is a SwiftUI View; `layout: .fixed(...)` is an option of the SwiftUI
// `.image` strategy. Views are @MainActor, so the test class is @MainActor too.
@MainActor
final class ItemRowSnapshotTests: XCTestCase {
    func test_itemRow_default() {
        let view = ItemRow(item: .fixture())
        assertSnapshot(of: view, as: .image(layout: .fixed(width: 375, height: 80)))
    }
}
```

## Practice Questions

- When do snapshot tests provide real value?

## Senior Take

Snapshot tests are high value for design systems and reusable components. They are lower value for full screens that change frequently. Run them in CI on a fixed simulator configuration to avoid false positives from rendering differences between machines.

## Practice Question Answers

### When do snapshot tests provide real value?

Snapshot tests provide real value when the UI is relatively stable, reused in many places, and must render correctly across many variants that a human cannot check by eye every time code changes.

The mechanism is simple: the test renders a view (like `ItemRow`) into an image, compares it pixel by pixel with a committed reference image, and fails if they differ. That way it catches bugs unit tests cannot see: misaligned padding, truncated text, wrong colours in dark mode, broken layout with large Dynamic Type or right-to-left languages.

Where they are worth it:

- Design-system components: buttons, badges, cells, a `PriceTagView` with regular, discounted and free states.
- Variant matrices: light/dark, several text sizes, several languages, small/large iPhones. One test can produce an image for each combination.
- UI refactors (for example moving from UIKit to SwiftUI) where you want the visuals to stay the same.

When they add little value: full screens whose design keeps changing, because every edit requires re-recording a batch of images and people start accepting them without looking. Snapshots also do not check logic, interaction or navigation; they only say "it looks the same as before".

Trade-off: images make the repo heavier and tests depend on the rendering environment (simulator, iOS version, Xcode). You need a fixed simulator configuration in CI and serious review of image diffs in pull requests.

## Interview Traps

### "A snapshot test fails after a merge. The quick fix is to re-record the images?"

**Common wrong answer:** Yes, snapshot failures usually just mean the UI changed, so re-record and commit.

**Better answer:** Re-recording without looking at the diff turns snapshot tests into a rubber stamp and removes the very reason they exist. On failure the library writes out the reference image, the new image and a diff; open them and decide whether the change is intentional or a regression. Only re-record when the change really is the intended design, and the pull request reviewer should review new reference images just like code.

### "I recorded images on my machine and committed them. Why does CI fail when nothing changed?"

**Common wrong answer:** CI is broken or the library has a bug; just lower `precision` until it passes.

**Better answer:** Rendering depends on the simulator model, the iOS runtime version, the Xcode version, screen scale, fonts and sometimes the machine architecture, so images from a dev machine and CI can differ by a few pixels due to anti-aliasing. The right fix is to pin one configuration (same simulator, same OS, same Xcode) for both recording and verifying, often by recording on CI itself or through a shared script. You can use `perceptualPrecision` (for example `0.98`) to ignore tiny differences the human eye cannot see; lowering `precision` too far also hides real regressions.

### "The first time a snapshot test runs, it passes, right?"

**Common wrong answer:** Yes, there is nothing to compare against the first time, so it passes, and to record you set the global `isRecording = true`.

**Better answer:** With swift-snapshot-testing, when no reference image exists, the library writes a new one and deliberately *fails* the test so you review the image before committing it. Every time the library writes a new image to disk, the test deliberately fails, even when recording is on. The way to enable recording has also changed: since version 1.17 there are four modes, `.missing` (the default: only record missing images), `.failed` (overwrite images of failing snapshots), `.all` (re-record everything) and `.never` (never record). Configure them with `withSnapshotTesting(record: .all) { ... }` (in XCTest usually wrapped in `override func invokeTest()`), the Swift Testing trait `.snapshots(record:)`, the `record:` parameter of `assertSnapshot` for a single assertion, or the `SNAPSHOT_TESTING_RECORD` environment variable (for example `SNAPSHOT_TESTING_RECORD=failed`). The old global `isRecording` is deprecated. In CI prefer `.never`: if a reference image is missing, the test fails with a clear message instead of silently creating a new image on the CI machine.

## Exercise

Add a snapshot test for a `PriceTagView` that displays a price string with a currency symbol. Test three variants: regular price, discounted price, and free. Then describe what CI setup is required to keep these tests from producing false positives across different machines.
