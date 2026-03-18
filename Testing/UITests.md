[English](./UITests.md) | [Tiếng Việt](./UITests.vi.md)

[← Testing](./README.md)

# UI Tests

## Key Idea

UI tests validate critical user flows end to end. They provide confidence that screens, navigation, and integration points still work after changes.

## What To Review

- Use UI tests for high-value flows, not every permutation
- Prefer stable accessibility identifiers
- Keep setup deterministic with launch arguments and stubbed data
- Avoid brittle timing assumptions

## Example

```swift
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

## Exercise

Pick one production-critical flow in your app. Define the launch setup, the accessibility identifiers it needs, and the assertions that make the test meaningful without overspecifying UI details.
