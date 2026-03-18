[English](./Protocols.md) | [Tiếng Việt](./Protocols.vi.md)

[← Swift Core](./README.md)

# Protocol-Oriented Programming

## Key Idea

Protocols help define behavior contracts and reduce coupling. They are especially useful for testability, composability, and API boundaries.

## Example

```swift
protocol UserRepository {
    func fetchUser(id: String) async throws -> User
}
```

## Good Senior Framing

- Protocols are helpful at boundaries
- Too many protocols can overcomplicate the codebase
- Protocols should exist for a real substitution or abstraction need

## Exercise

Define an `AnalyticsService` protocol with a single method `track(event: String)`. Write two conforming types: `FirebaseAnalytics` (which just prints "Firebase: \(event)") and `NoOpAnalytics` (which does nothing). Inject `AnalyticsService` into a `CheckoutViewModel` via its initializer. Write a unit test using `NoOpAnalytics`. Explain why the protocol boundary makes the ViewModel testable.
