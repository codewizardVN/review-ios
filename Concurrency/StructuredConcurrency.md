[English](./StructuredConcurrency.md) | [Tiếng Việt](./StructuredConcurrency.vi.md)

[← Concurrency](./README.md)

# Structured Concurrency

## Key Idea

Structured concurrency ties the lifetime of child tasks to their parent scope. When the parent scope exits — whether normally or via cancellation — child tasks are automatically cancelled.

## What To Review

- `async let` — start concurrent work and await later
- `withTaskGroup` / `withThrowingTaskGroup` — dynamic fan-out
- Task hierarchy — parent cancels children automatically
- Task priority propagation

## Example

```swift
func loadDashboard() async throws -> Dashboard {
    async let user = fetchUser()
    async let feed = fetchFeed()
    return try await Dashboard(user: user, feed: feed)
}
```

```swift
func fetchAll(ids: [String]) async throws -> [Item] {
    try await withThrowingTaskGroup(of: Item.self) { group in
        for id in ids {
            group.addTask { try await fetchItem(id: id) }
        }
        return try await group.reduce(into: []) { $0.append($1) }
    }
}
```

## Practice Questions

- When is async let clearer for a loadProfile() function that fetches user, posts, and followers concurrently, and when does withThrowingTaskGroup become necessary instead?

## Senior Take

Structured concurrency is not just a syntax convenience. It provides a clear ownership model: tasks are scoped, leaks are harder to introduce, and cancellation propagates automatically. Prefer it over unstructured `Task { }` whenever the lifetime is bounded.

## Exercise

Write a `loadProfile() async throws -> Profile` function that fetches `user`, `posts`, and `followers` concurrently using `async let`. Then rewrite the same function using `withThrowingTaskGroup` so the set of requests can be driven by a dynamic array. Write a comment comparing the two: when is `async let` clearer, and when does `TaskGroup` become necessary?
