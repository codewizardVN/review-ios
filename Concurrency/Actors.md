[English](./Actors.md) | [Tiếng Việt](./Actors.vi.md)

[← Concurrency](./README.md)

# Actor and MainActor

## Key Idea

`Actor` serializes access to its mutable state, preventing data races without manual locks. `@MainActor` guarantees code runs on the main thread.

## What To Review

- `actor` — reference type with isolated mutable state
- `@MainActor` — annotation to pin a class, function, or property to the main thread
- Actor reentrancy — a suspended `await` inside an actor can allow other work to run
- `nonisolated` — opt out of actor isolation for specific members

## Example

```swift
actor ImageCache {
    private var cache: [URL: UIImage] = [:]

    func image(for url: URL) -> UIImage? {
        cache[url]
    }

    func store(_ image: UIImage, for url: URL) {
        cache[url] = image
    }
}

@MainActor
final class FeedViewModel: ObservableObject {
    @Published var items: [FeedItem] = []
}
```

## Practice Questions

- When can bugs still happen even if you use `Actor`?

## Senior Take

Actor reentrancy is the most common surprise. State can change between two `await` points inside the same actor method, so do not assume state is stable across suspensions.

## Exercise

Implement an `actor RequestCounter` with `func increment()`, `func decrement()`, and `var count: Int`. Spawn 100 concurrent `Task { }` blocks that each call `increment()` then `decrement()`. Assert the final count is 0. Then deliberately introduce a reentrancy bug by inserting an `await` between increment and decrement. Explain in a comment what state corruption becomes possible and why.
