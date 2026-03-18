[English](./Mocking.md) | [Tiếng Việt](./Mocking.vi.md)

[← Testing](./README.md)

# Mocking and Test Doubles

## Types of Test Doubles

| Type | Description |
| --- | --- |
| **Stub** | Returns a fixed value; does not verify calls |
| **Mock** | Verifies that specific calls were made |
| **Fake** | Lightweight working implementation (e.g. in-memory repository) |
| **Spy** | Records calls for later assertion |

## Preferred Approach in Swift

Use protocol-based fakes. Define a protocol, implement the real version in production, and implement a `Fake` version in tests.

```swift
protocol FeedRepository {
    func fetchFeed() async throws -> [FeedItem]
}

// Test fake
final class FakeFeedRepository: FeedRepository {
    var stubbedItems: [FeedItem] = []
    var fetchCallCount = 0

    func fetchFeed() async throws -> [FeedItem] {
        fetchCallCount += 1
        return stubbedItems
    }
}
```

## Practice Questions

- How do mocks differ from stubs?
- Should you use a mocking framework or write fakes manually?

## Senior Take

Manual fakes are usually clearer and safer than generated mocks. Mocking frameworks can obscure what is actually being tested. Reserve them for cases where the fake would be prohibitively complex to write by hand.

## Exercise

Create a `FakeAnalyticsService` that records every event name passed to it. Inject it into a `CheckoutViewModel` and assert that `trackPurchase()` is called exactly once after a successful order. Then explain: is this a mock, a stub, or a spy?
