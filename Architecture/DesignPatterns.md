[English](./DesignPatterns.md) | [Tiếng Việt](./DesignPatterns.vi.md)

[← Architecture](./README.md)

# Design Patterns

## Key Idea

MVC/MVVM/Clean Architecture describe how a whole app or feature is structured. Below that level, classic design patterns solve smaller, recurring problems inside those layers — knowing them by name and trade-off matters in code review.

## What To Review

- **Factory** — centralize object creation so call sites don't know concrete types (e.g., `ViewModelFactory` producing a view model with its dependencies already injected)
- **Repository** — abstracts data source (network, cache, database) behind a protocol so the rest of the app doesn't care where data comes from
- **Observer** — `NotificationCenter`, Combine's `Publisher`, and `@Published` are all variations of this; decouples a producer of events from consumers
- **Strategy** — swap an algorithm/behavior at runtime behind a shared protocol (e.g., different validation strategies per form field type)
- **Adapter** — wrap a legacy or third-party API behind an interface your app actually wants (common when bridging an old Objective-C SDK into a modern async interface)
- **Singleton** — genuinely useful for a small number of true app-wide services (e.g., a logger), but overused as a shortcut around proper dependency injection — a code review red flag when applied to anything with meaningful state or that needs to be faked in tests

## Example

```swift
protocol OrderRepository {
    func fetchOrders() async throws -> [Order]
}

final class RemoteOrderRepository: OrderRepository {
    private let client: APIClient
    init(client: APIClient) { self.client = client }

    func fetchOrders() async throws -> [Order] {
        try await client.get("/orders")
    }
}

final class InMemoryOrderRepository: OrderRepository {
    func fetchOrders() async throws -> [Order] { [] }
}
```

## Practice Questions

- Why does a `Repository` protocol matter more for testability than for the production implementation itself?
- When is a Singleton the right call, and when is it a sign that dependency injection was skipped?

## Senior Take

Naming a pattern isn't the point — recognizing when a pattern is being misapplied is. The most common code review finding at senior level is Singleton creep: services that hold meaningful mutable state get exposed as `.shared`, which makes unit testing nearly impossible and hides implicit coupling across unrelated features. A senior engineer pushes these back toward constructor-injected dependencies even when it's more typing upfront.

## Practice Question Answers

### Why does a `Repository` protocol matter more for testability than for the production implementation itself?

Because in production there is almost always just one implementation, `RemoteOrderRepository`; the protocol's everyday value is the "seam" it creates so tests and previews can substitute `InMemoryOrderRepository`.

Mechanism: the ViewModel or use case depends on `OrderRepository`, not on a concrete type. The composition root decides which one to plug in. In tests you plug in the in-memory version that returns a ready-made list of orders or throws, so you can check display logic, the empty state, and the error state without a network. SwiftUI previews reuse the same fake.

The commonly cited reason is "later, switching from REST to GraphQL or adding a cache only needs a new implementation". That's real but rare, and when it happens the protocol's shape usually has to change too: pagination, caching, and offline support make the abstraction leak. So be honest: the protocol is justified mainly by tests and previews.

Trade-offs and doing it right:

- Design the protocol around the consumer's needs (`fetchOrders()`), don't copy the endpoint list.
- If a piece never needs replacing in tests, such as a pure mapping function, it doesn't need a protocol.
- A lighter seam also works: inject a closure `fetchOrders: () async throws -> [Order]` or a struct of closures.

### When is a Singleton the right call, and when is it a sign that dependency injection was skipped?

A Singleton is right when there is by nature only one instance and its state doesn't affect test outcomes; it's a sign DI was skipped when `.shared` holds meaningful mutable state and is called deep inside classes.

Reasonable cases: a logger (e.g. wrapping `os.Logger`), system objects like `FileManager.default`, `NotificationCenter.default`, `UIApplication.shared`. They carry almost no business state, and tests don't need to verify them.

Warning signs:

- `.shared` holds the session, the cart, a token, a cache.
- Tests have to "reset" the singleton between cases, or results depend on run order.
- Looking at a class's `init` doesn't tell you what it actually uses.

Separate two things: "only one instance" is about lifetime, while "accessed through a global" is about coupling. You can keep a single instance and still inject it: create it once at the composition root and pass it through `init`, or use a default argument `init(analytics: AnalyticsProtocol = AnalyticsService.shared)` during migration. In the Swift 6 language mode, `static let shared` of a non-`Sendable` class also gets a concurrency-safety error from the compiler (unless the class is isolated to a global actor such as `@MainActor`, including when that is inferred from Swift 6.2's default `MainActor` isolation), forcing you to rethink the design.

## Interview Traps

### "Is `static let shared = NetworkManager()` thread-safe?"

**Common wrong answer:** "No, you must wrap it in `dispatch_once` or a lock," or the opposite, "yes, so the whole class is safe."

**Better answer:** Swift initializes `static let` lazily and thread-safely (via `swift_once`), so the instance is created only once. But that covers only initialization; mutable state inside, like a token or cache, still has data races if several threads read and write it. Swift 6 strict concurrency errors on `static var` and on `static let` of a non-`Sendable` type; fix it by making it an `actor`, marking it `@MainActor`, or protecting the state with `Mutex` (Synchronization module, iOS 18+).

### "An observer registered with `NotificationCenter` must call `removeObserver` in `deinit`?"

**Common wrong answer:** "You always have to remove it or it crashes." This is outdated knowledge.

**Better answer:** Since iOS 9, selector-based observers (`addObserver(_:selector:name:object:)`) are automatically unregistered when deallocated. The real trap is the block-based `addObserver(forName:object:queue:using:)`: it returns a token you must keep and remove yourself, and a closure capturing `self` strongly keeps the object alive forever so `deinit` never runs. For new code, `NotificationCenter.default.notifications(named:)` inside a `Task`, or a Combine publisher with an `AnyCancellable`, makes lifetime easier to manage.

### "I call `publisher.sink { ... }` without storing the result; why don't I receive any values?"

**Common wrong answer:** "The publisher hasn't emitted yet," or "it's running on the wrong thread."

**Better answer:** `sink` returns an `AnyCancellable`, and when that object is deallocated the subscription is cancelled. If you don't store it (the compiler only warns "result unused"), the subscription dies right after that line. A publisher that emits synchronously on subscription (such as `Just` or `CurrentValueSubject`) can still deliver its first value before the cancellation, so this bug usually shows up with values that arrive asynchronously, like a network response or a timer. Keep it, e.g. `.store(in: &cancellables)` with `cancellables` as a property of the object, and use `[weak self]` in the closure to avoid a retain cycle.

## Exercise

Refactor (in comments/pseudocode) a `NetworkManager.shared` singleton that handles auth token refresh, request building, and caching all in one class. Split it using Repository (per-resource data access), Strategy (retry policy pluggable per endpoint type), and constructor injection instead of a shared singleton. Explain what becomes testable that wasn't before.
