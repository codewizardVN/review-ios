[English](./UITests.md) | [Tiếng Việt](./UITests.vi.md)

[← Testing](./README.md)

# UI Tests

## Key Idea

UI tests validate critical user flows end to end. They provide confidence that screens, navigation, and integration points still work after changes.

## What To Review

- Use UI tests for high-value flows, not every permutation: UI tests are slow and flaky-prone, so reserve them for a few key journeys; variations (bad email, server errors...) belong in unit tests.
- Prefer stable accessibility identifiers: find elements by `accessibilityIdentifier` (for example `login.email`) instead of display text, which changes with language and copy.
- Keep setup deterministic with launch arguments and stubbed data: the test passes flags via `launchArguments`/`launchEnvironment`, and the app reads them at startup to use fake data instead of the real backend, so every run gives the same result.
- Avoid brittle timing assumptions: no fixed `sleep`; wait on conditions with `waitForExistence(timeout:)` or expectations.
- UI tests run in a separate process and drive the app through accessibility (XCUITest), so they cannot reach objects inside the app directly.

## Example

```swift
// Since Xcode 16, XCUIApplication/XCUIElement are @MainActor, so the test method
// (or the whole class) needs @MainActor to compile in the Swift 6 language mode.
@MainActor
func test_login_success_showsHomeScreen() {
    let app = XCUIApplication()
    app.launchArguments = ["-ui-test-login-success"]
    app.launch()

    app.textFields["login.email"].tap()
    app.textFields["login.email"].typeText("hello@example.com")
    app.secureTextFields["login.password"].tap()
    app.secureTextFields["login.password"].typeText("123456")
    app.buttons["login.submit"].tap()

    XCTAssertTrue(app.staticTexts["home.title"].waitForExistence(timeout: 2))
}
```

## Practice Questions

- Which flows deserve UI tests first?
- How do you reduce flaky UI tests?

## Senior Take

UI tests are expensive. Use them to protect a few business-critical journeys like login, checkout, onboarding, or a risky migration. The goal is confidence per cost, not blanket coverage.

## Practice Question Answers

### Which flows deserve UI tests first?

Prioritize flows where a break costs money, costs users, or leaves users stuck: usually login, first-run onboarding, checkout/payment, and flows that run after a risky data migration.

How to choose: multiply "damage if it breaks" by "chance it breaks in a way unit tests would not catch". UI tests are strongest at checking pieces *wired together*: navigation, deep links, the right screen being pushed, the keyboard, permission alerts, data flowing across several screens. Unit tests of individual ViewModels cannot see these.

A good first test usually looks like the `test_login_success_showsHomeScreen` example: a short happy path, going from the first screen to the result the user cares about, asserting one meaningful thing (the Home screen appears).

Do not use UI tests for every permutation: invalid email format, short password, ten kinds of server error. Those branches belong in unit tests for `LoginViewModel`, which are far faster and more stable. UI tests are slow (seconds to tens of seconds each), consume CI time and flake easily, so each one must earn its cost. A small set of 5–15 UI tests for the key journeys usually gives more confidence than 200 tests covering every screen.

### How do you reduce flaky UI tests?

Reduce flakiness by removing everything non-deterministic: data, timing, leftover state and how elements are located.

- **Fixed data**: pass `launchArguments` or `launchEnvironment` (like `-ui-test-login-success`) so the app uses a stub server or local data instead of the real backend. The real network is the number one source of flakiness.
- **Wait on conditions, not time**: use `waitForExistence(timeout:)` or `XCTNSPredicateExpectation` instead of `sleep`. The test waits exactly until the element appears, no longer.
- **Clean state**: each test launches the app with reset state so it does not depend on the previous test. The test runner cannot delete data inside the app, so the usual approach is to pass a flag (for example `-reset-state`) and have the app, when it sees that flag, clear the keychain, use a separate `UserDefaults(suiteName:)` for tests and a temporary database.
- **Stable selectors**: use an `accessibilityIdentifier` like `login.email`, not display text, which changes with language and copy.
- **Disable animations** when the app runs in UI-test mode to cut transition waits, for example the app calls `UIView.setAnimationsEnabled(false)` when it receives the matching launch argument.
- **Handle system alerts** (location, notification permissions...): use `addUIInterruptionMonitor` (the handler only runs when the test interacts with the app again, so after the alert appears you need an action such as `app.tap()`), or find the alert through `XCUIApplication(bundleIdentifier: "com.apple.springboard")`, or pre-grant permissions on the simulator with `xcrun simctl privacy` before the run.

Trade-off: stubbing too much means UI tests no longer catch integration bugs with the real backend. Many teams keep an extra small suite that runs against staging, separate from the main pipeline so flakiness there does not block merges.

## Interview Traps

### "A test fails occasionally because the screen has not loaded in time. Can we add `sleep(3)`?"

**Common wrong answer:** Yes, just make the wait long enough and the test will be stable.

**Better answer:** `sleep` is both slow and does not fix the root cause: on a busy CI machine it may still not be enough, and on a fast machine it wastes time on every run. Wait on a condition instead, for example `XCTAssertTrue(app.staticTexts["home.title"].waitForExistence(timeout: 5))`, because it returns as soon as the element appears. To wait for an element to disappear, XCTest has `waitForNonExistence(timeout:)` since Xcode 16 (it returns `Bool`, so wrap it in `XCTAssertTrue`); with older Xcode versions use `XCTNSPredicateExpectation` with an `exists == false` predicate.

### "In a UI test, can you inject a `FakeAuthService` into the ViewModel like in a unit test?"

**Common wrong answer:** Yes, just `@testable import` the app and assign the fake to the ViewModel before tapping.

**Better answer:** No. UI tests run in a separate process (the test runner) and drive the app through accessibility, so they cannot reach objects inside the app, even with `@testable import`. The right way is to pass a signal through `launchArguments`/`launchEnvironment`; the app reads `ProcessInfo.processInfo.arguments` at startup and picks fake dependencies itself. Put that code behind `#if DEBUG` so it does not ship in release builds.

### "Is there a problem with finding a button via `app.buttons["Log In"]`?"

**Common wrong answer:** No, display text is readable and matches how the user sees the screen.

**Better answer:** Display text changes with localization and copy edits, and can collide between several elements, so the test breaks even though behaviour did not change. Assign a stable `accessibilityIdentifier` like `login.submit`; identifiers are not read by VoiceOver, so they do not affect users. Do not put identifiers into `accessibilityLabel`, because the label is what VoiceOver reads to users and must be natural language.

## Exercise

Pick one production-critical flow in your app. Define the launch setup, the accessibility identifiers it needs, and the assertions that make the test meaningful without overspecifying UI details.
