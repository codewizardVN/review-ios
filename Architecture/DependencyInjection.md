[English](./DependencyInjection.md) | [Tiếng Việt](./DependencyInjection.vi.md)

[← Architecture](./README.md)

# Dependency Injection

## Key Idea

Pass dependencies in from the outside rather than creating them internally. This makes components testable, replaceable, and explicit about what they need.

## Approaches

### 1. Constructor injection (preferred)

```swift
final class FeedViewModel {
    private let repository: FeedRepository

    init(repository: FeedRepository) {
        self.repository = repository
    }
}
```

### 2. Property injection

```swift
final class FeedViewModel {
    var repository: FeedRepository = RemoteFeedRepository()
}
```

### 3. Environment / Service Locator

Useful in SwiftUI via `.environment()` or a shared container, but hides dependencies and can make flow harder to trace.

## Why It Matters

- Swap real implementations for fakes in tests
- Explicit dependencies are self-documenting
- No hidden global state

## Practice Questions

- How does dependency injection help testing?
- What criteria would you use to decide between a DI container and manual injection?

## Senior Take

Manual DI is usually enough for most apps. Reach for a DI container (like Needle or Swinject) only when the dependency graph is large and complex. Containers add their own complexity and learning curve.

## Exercise

Take a `CheckoutViewModel` that calls `PaymentService()` and `AnalyticsService.shared` internally. Refactor it: (1) extract `PaymentServiceProtocol` and `AnalyticsProtocol`, (2) move to constructor injection. Write two tests: one verifying analytics tracks `"purchase_complete"` on payment success, one verifying it does NOT track on failure. Explain why constructor injection is preferred over property injection for required dependencies.
