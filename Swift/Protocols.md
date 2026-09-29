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

- Protocols are helpful at boundaries: between a ViewModel and the network/storage layer, or between modules — where you want to swap implementations (real, test, offline) without changing the calling code.
- Too many protocols can overcomplicate the codebase: every protocol is a layer of indirection, and readers have to jump back and forth between protocol and implementation.
- Protocols should exist for a real substitution need (swapping implementations, e.g. for tests) or a real abstraction need (several types genuinely share a behavior), not "because POP says so".

## Practice Questions

- Why does injecting an AnalyticsService protocol (with FirebaseAnalytics and NoOpAnalytics implementations) into a CheckoutViewModel's initializer make the ViewModel testable?

## Practice Question Answers

### Why does injecting an AnalyticsService protocol (with FirebaseAnalytics and NoOpAnalytics implementations) into a CheckoutViewModel's initializer make the ViewModel testable?

Because `CheckoutViewModel` depends only on a contract, not on Firebase, a test can pass in a different implementation that never calls the SDK, needs no network, sends no real events, and gives the same result every run.

The mechanism: if the ViewModel created `FirebaseAnalytics()` internally, a test would have no way to replace it. When the dependency comes through the initializer, whoever creates the ViewModel decides which implementation to use: the app uses `FirebaseAnalytics`, the test uses `NoOpAnalytics`. Note that `NoOpAnalytics` only lets you test other logic without side effects; to check that "tapping pay tracks the right event" you need a spy that records events.

```swift
final class CheckoutViewModel {
    private let analytics: any AnalyticsService
    init(analytics: any AnalyticsService) { self.analytics = analytics }
    func pay() { analytics.track(event: "checkout_pay") }
}

final class SpyAnalytics: AnalyticsService {
    private(set) var events: [String] = []
    func track(event: String) { events.append(event) }
}
```

Trade-off: every protocol is a layer of indirection the reader has to follow. Create protocols only at boundaries with real side effects (network, analytics, storage, time). In Swift 6, if the ViewModel is `@MainActor` and the service is used from several places, you also have to think about whether the protocol needs to be `Sendable`.

## Interview Traps

### "Which version runs when a protocol extension method is called through any P?"

**Common wrong answer:** Always the conforming type's version, because Swift uses dynamic dispatch like class overrides.

**Better answer:** It depends on whether the method is a requirement. If it is declared in the protocol, the call goes through the witness table and runs the conforming type's version. If the method exists only in an extension and not in the protocol declaration, it is dispatched statically by the variable's static type: calling it through `any AnalyticsService` always runs the extension version, even if `FirebaseAnalytics` has a method with the same name. To make it "overridable", put the method in the protocol declaration.

### "A protocol with an associatedtype can't be used as a variable type, right?"

**Common wrong answer:** Right, you still get "can only be used as a generic constraint" and must use type erasure like `AnyPublisher` in every case.

**Better answer:** That is pre-Swift 5.7 knowledge. Since Swift 5.7, SE-0309 lets you declare `any Collection` (an existential for a protocol with associated types/`Self`), and SE-0346 (primary associated types) lets you write `any Collection<Int>` or `some Collection<Int>`. However, through an existential you cannot call methods that take an associated type or `Self` as a parameter (the compiler does not know the concrete type inside); then you pass the existential to a generic function (Swift 5.7 opens it implicitly, SE-0352) or use hand-written type erasure. Type erasure like `AnyPublisher` is still useful for hiding a concrete type in an API, but it is no longer the only option.

### "Every class should have a protocol so it is easy to mock, right?"

**Common wrong answer:** Yes, POP means creating a protocol for every service/manager, each with its own mock.

**Better answer:** A protocol with one real implementation and one mock is often just extra indirection: harder "jump to definition", and the protocol and class drift apart. Create protocols at boundaries with side effects or with several real implementations. For small dependencies, passing a closure (`track: (String) -> Void`) or a struct of closures is often simpler and still testable.

## Exercise

Define an `AnalyticsService` protocol with a single method `track(event: String)`. Write two conforming types: `FirebaseAnalytics` (which just prints "Firebase: \(event)") and `NoOpAnalytics` (which does nothing). Inject `AnalyticsService` into a `CheckoutViewModel` via its initializer. Write a unit test using `NoOpAnalytics`. Explain why the protocol boundary makes the ViewModel testable.
