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

## Exercise

Refactor (in comments/pseudocode) a `NetworkManager.shared` singleton that handles auth token refresh, request building, and caching all in one class. Split it using Repository (per-resource data access), Strategy (retry policy pluggable per endpoint type), and constructor injection instead of a shared singleton. Explain what becomes testable that wasn't before.
