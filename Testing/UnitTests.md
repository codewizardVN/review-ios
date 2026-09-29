[English](./UnitTests.md) | [Tiếng Việt](./UnitTests.vi.md)

[← Testing](./README.md)

# Unit Tests

## Key Idea

Unit tests verify a single unit of behavior in isolation, without real network, database, or UI.

## What To Review

- XCTest — `XCTestCase`, `XCTAssert*`: the traditional test framework; each test is a method whose name starts with `test`, checked with functions like `XCTAssertEqual`, `XCTAssertTrue`, `XCTAssertThrowsError`...
- Swift Testing (since Xcode 16) — `@Test`, `@Suite`, `#expect`, `#require`: Apple's newer framework, which uses macros instead of method names, runs tests in parallel by default and supports parameterized tests (`@Test(arguments:)`). Both frameworks can live in the same test target.
- Given / When / Then structure: split a test into three clear parts — set up data and dependencies (Given), call the action under test (When), check the result (Then) — so a reader immediately sees what the test checks.
- Testing ViewModels through inputs and outputs: call the ViewModel's public methods (input) and assert on the state it exposes (output), not on its internals.
- Async testing: if the code is `async`, mark the test `async` and `await` it directly (both XCTest and Swift Testing support this). `XCTestExpectation` + `fulfillment(of:timeout:)` (or `wait(for:timeout:)` in synchronous code) is for callback/delegate-style APIs; Swift Testing uses `confirmation` to count how many times an event happens, but it does not wait like an expectation: the event must happen before the `confirmation` closure returns, so a callback should be wrapped as `async` (for example with `withCheckedContinuation`) and awaited inside the closure.

## Example

```swift
import XCTest
@testable import MyApp

// ViewModels are usually @MainActor, so the test class is marked @MainActor too,
// letting it read `sut.items` without an isolation error in Swift 6.
@MainActor
final class FeedViewModelTests: XCTestCase {
    func test_load_populatesItems() async throws {
        // Given
        let repository = FakeFeedRepository(items: [.fixture()])
        let sut = FeedViewModel(repository: repository)

        // When
        await sut.load()

        // Then
        XCTAssertEqual(sut.items.count, 1)
    }
}
```

## Practice Questions

- Which tests should be written and which should not?
- If code is hard to test, where is the problem usually located?

## Senior Take

Hard-to-test code is usually a design signal: the code has hidden dependencies, global state, or mixed concerns. Test difficulty should prompt a refactor, not a workaround.

## Practice Question Answers

### Which tests should be written and which should not?

Write tests for logic that makes decisions and carries risk; thin "wiring" code and framework behaviour do not need their own tests.

A simple filter: ask "if this is wrong, does the user or the business get hurt, and could the bug slip through review?". Things worth testing:

- Business rules: price calculation, form validation, permission rules.
- ViewModel state transitions: loading → loaded → error, like `FeedViewModel.load()` in the example.
- Mapping and parsing: JSON → model, model → display text.
- Edge cases and error paths: empty list, network failure, expired token.
- Bugs that already happened: write a test that reproduces the bug before fixing it, so it never comes back.

Not worth a dedicated test: trivial getters/setters, initializers that only assign properties, code that just forwards a call to a dependency, and Apple framework behaviour (you do not need to test that `Array.sorted()` sorts). Pure layout is also a poor fit for unit tests; snapshot or UI tests fit better.

Trade-off: tests are code you must maintain. Tests coupled to implementation details (for example asserting the order of private method calls) break on every refactor without catching real bugs. Test observable behaviour through inputs and outputs, not how the code works internally.

### If code is hard to test, where is the problem usually located?

The problem is usually in the design, specifically in how the code obtains its dependencies and where it puts side effects, and rarely in the testing tools.

Common causes:

- **Hidden dependencies**: the code calls `URLSession.shared`, `UserDefaults.standard`, `Date()` or a singleton directly. Tests cannot replace them with fakes, so they must hit the real network or depend on the system clock.
- **Global mutable state**: several tests write to the same place, so results depend on execution order. With Swift Testing running in parallel by default, this shows up even faster.
- **Mixed responsibilities**: one class calls the API, parses, formats text and drives the UI. To test one part you must build the whole thing.
- **Logic inside the UI**: logic in `viewDidLoad` or `body` needs a view hierarchy to run.

The fix is to inject dependencies through the initializer (like `FeedViewModel(repository:)`), keep pure logic separate from I/O, and split big classes into small units. With the right design, tests almost write themselves: create a fake, call a method, check the output.

When not to refactor right away: a large legacy codebase with no tests. Then write a few higher-level characterization tests to lock in current behaviour first, and extract pieces gradually.

## Interview Traps

### "Our team has 90% coverage. Is the test suite good?"

**Common wrong answer:** High coverage means the code is well tested, so 90% is good and we should push to 100%.

**Better answer:** Coverage only measures which lines were *executed* during tests, not whether the tests *assert* the things that matter. A test that calls `sut.load()` with no assertion still raises coverage. Coverage is useful for finding untested areas, but it is not a quality metric; hard targets tend to produce meaningless tests. Quality should be judged by whether tests catch real bugs, for example through mutation testing or reviewing assertions.

### "The ViewModel calls `Task { await load() }` inside `onAppear()`. The test calls `sut.onAppear()` and asserts immediately. What is wrong?"

**Common wrong answer:** Nothing, because the test is `async`, so it automatically waits for the work inside to finish.

**Better answer:** `Task { }` creates an unstructured task; `onAppear()` returns immediately without waiting for it, so the test asserts before the data arrives and fails or becomes flaky. The best fix is for the ViewModel to expose an `async` function (like `await sut.load()` in the example) that the test awaits directly, or to keep a reference to the task so the test can `await task.value`. Avoid fixing it with `Task.sleep` in the test, because that is just guessing the timing.

### "In XCTest, are the test class's properties shared between test methods?"

**Common wrong answer:** Yes, XCTest creates one instance for the whole class, so you must reset state in `setUp()` so tests do not affect each other.

**Better answer:** XCTest creates a separate instance for *each* test method, so stored properties are not shared. The real gotcha is that XCTest keeps all those instances alive until the whole suite finishes, so heavy objects or objects with side effects are not released early; that is why you set them to `nil` in `tearDown()`. Swift Testing also creates a fresh instance for each `@Test`, and a suite that is a class or actor can use `deinit` for cleanup. What really is shared is static and global state, and that is where you need to be careful.

## Exercise

Write a unit test for a `LoginViewModel` that has a `login(email:password:)` method. Use a `FakeAuthService` to stub a successful response. Structure your test with Given / When / Then. Then write a second test for the failure path — assert that `errorMessage` is set when the service throws.
