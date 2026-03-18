[English](./UnitTests.md) | [Tiếng Việt](./UnitTests.vi.md)

[← Testing](./README.md)

# Unit Tests

## Key Idea

Unit tests verify a single unit of behavior in isolation, without real network, database, or UI.

## What To Review

- XCTest — `XCTestCase`, `XCTAssert*`
- Given / When / Then structure
- Testing ViewModels through inputs and outputs
- Async testing with `async/await` or `XCTestExpectation`

## Example

```swift
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

## Exercise

Write a unit test for a `LoginViewModel` that has a `login(email:password:)` method. Use a `FakeAuthService` to stub a successful response. Structure your test with Given / When / Then. Then write a second test for the failure path — assert that `errorMessage` is set when the service throws.
