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

## Practice Question Answers

### How does dependency injection help testing?

DI lets a test replace real dependencies with fakes the test controls, so tests run fast, stay deterministic, and can cover cases that are hard to reproduce.

When `CheckoutViewModel` creates `PaymentService()` and calls `AnalyticsService.shared` itself, a test has no way to step in: payment hits the real network, analytics sends real events, and singleton state leaks between tests. When dependencies come in through `init`, the test decides what they return and records the calls:

```swift
final class SpyAnalytics: AnalyticsProtocol {
    private(set) var events: [String] = []
    func track(_ event: String) { events.append(event) }
}

let analytics = SpyAnalytics()
let vm = CheckoutViewModel(payment: StubPayment(result: .failure(.declined)),
                           analytics: analytics)
await vm.pay()
XCTAssertTrue(analytics.events.isEmpty)
```

Concrete benefits: (1) you control the inputs, such as a declined payment or a timeout, without a server; (2) you can observe the outputs, such as which events were tracked; (3) each test gets its own objects and doesn't depend on run order.

Trade-off: mocking too much ties tests to implementation details, so changing internals breaks tests even when behaviour hasn't changed. Only fake at boundaries with side effects (network, storage, time, analytics); use the real thing for pure pieces like formatters.

### What criteria would you use to decide between a DI container and manual injection?

Default to manual injection through `init` and a composition root; reach for a container only when the wiring itself has become a measurable pain.

Criteria to look at:

- **Graph size and depth**: having to pass one dependency through four or five layers just so the bottom layer can use it is a sign manual wiring is getting expensive.
- **Number of scopes and lifetimes**: app-wide, per login session, per flow. Managing many scopes by hand is error-prone.
- **Modularization**: feature modules need to be built without knowing concrete types from other modules.
- **Compile-time safety**: with manual DI a missing dependency is a compile error. With a runtime-resolving container like Swinject, a forgotten registration only shows up at run time: `resolve` returns `nil`, and since code usually force-unwraps it (`resolve(...)!`), the result is a crash. Needle generates code, so it keeps compile-time checks at the cost of an extra build step.
- **Team**: a container is one more thing everyone has to learn and debug.

A useful intermediate step before a container: group each feature's dependencies into a `Dependencies` struct or a factory and pass that struct down. This cuts the parameter threading while keeping compile-time safety.

## Interview Traps

### "Is calling `Container.shared.resolve(PaymentServiceProtocol.self)` inside a class dependency injection?"

**Common wrong answer:** "Yes, because it uses a DI container."

**Better answer:** That is a Service Locator, close to the opposite of DI: the class still fetches its dependencies from a global, so you can't tell from `init` what it needs, and a missing registration only shows up at run time. DI means the class receives its dependencies from outside. The container should only be called at the composition root to build objects, not scattered through the code.

### "Is property injection with a default value just as testable as constructor injection?"

**Common wrong answer:** "Same thing, the test just assigns `vm.repository = FakeFeedRepository()`."

**Better answer:** With `var repository: FeedRepository = RemoteFeedRepository()`, the real instance is created before the test gets a chance to replace it; if its `init` has side effects (reading the keychain, opening a connection), they still happen. The object can also be used before the right dependency is assigned, and the property must be `var` instead of `let`, which Swift 6 often flags when the class needs to be `Sendable`. Constructor injection guarantees the object is complete and immutable as soon as it is created.

### "Is SwiftUI `@Environment` as safe as injecting through `init`?"

**Common wrong answer:** "Same thing, just shorter syntax."

**Better answer:** For an `@Observable` object, reading `@Environment(CartModel.self)` without an ancestor calling `.environment(cart)` crashes at run time; `@EnvironmentObject` does the same. An `EnvironmentKey` with a `defaultValue` won't crash but silently uses the default, which might be the production implementation inside a preview or test. Environment suits cross-cutting dependencies like theme or locale; a screen's required dependencies should go through `init` so the compiler checks them.

## Exercise

Take a `CheckoutViewModel` that calls `PaymentService()` and `AnalyticsService.shared` internally. Refactor it: (1) extract `PaymentServiceProtocol` and `AnalyticsProtocol`, (2) move to constructor injection. Write two tests: one verifying analytics tracks `"purchase_complete"` on payment success, one verifying it does NOT track on failure. Explain why constructor injection is preferred over property injection for required dependencies.
