[English](./Actors.md) | [Tiếng Việt](./Actors.vi.md)

[← Concurrency](./README.md)

# Actor and MainActor

## Key Idea

`Actor` serializes access to its mutable state, preventing data races without manual locks. `@MainActor` guarantees code runs on the main thread.

## What To Review

- `actor` — a reference type whose mutable state is isolated: outside code can only reach it via `await`, and the actor runs at most one piece of its code at a time, so there are no data races.
- `@MainActor` — the global actor tied to the main thread; mark a class, function or property with it so the compiler forces every access from elsewhere to hop to the main thread.
- Actor reentrancy — when an actor method hits `await` and suspends, the actor is released to run other calls; when the method resumes, the state may have changed.
- `nonisolated` — opt specific members out of actor isolation (for example a computed property that only reads immutable `let` data) so they can be called without `await`; such a member cannot touch the actor's mutable state.

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

## Practice Question Answers

### When can bugs still happen even if you use `Actor`?

An actor only prevents memory-level data races (two threads writing the same variable); it does not prevent logic-level races, and the biggest source of bugs is reentrancy at every `await`.

Mechanism: an actor runs only one piece of its code at a time, but when an actor method hits `await`, it releases the actor and other calls can run in between. When it resumes, the state may have changed. For example, extend `ImageCache` with a loading method:

```swift
func load(_ url: URL) async throws -> UIImage {
    if let cached = cache[url] { return cached }
    let image = try await download(url)   // actor is released here
    cache[url] = image                    // another caller may have written first
    return image
}
```

Two callers calling `load` for the same URL will download twice. The fix is to store the in-flight `Task` in a dictionary so later callers `await` the same task, and always re-check state after every `await`:

```swift
private var inFlight: [URL: Task<UIImage, Error>] = [:]

func load(_ url: URL) async throws -> UIImage {
    if let cached = cache[url] { return cached }
    if let task = inFlight[url] { return try await task.value }   // share the download already running
    let task = Task { try await download(url) }
    inFlight[url] = task          // written before any await: no gap
    defer { inFlight[url] = nil }
    let image = try await task.value
    cache[url] = image
    return image
}
```

Other cases:
- Check-then-act from outside: `if await cache.image(for: url) == nil { await cache.store(...) }` is two separate calls, and another caller can slip in between.
- Returning a non-`Sendable` reference type from an actor and then mutating it outside without protection. In Swift 6 language mode the compiler usually blocks this; but in Swift 5 mode, or when the type is marked `@unchecked Sendable` / imported via `@preconcurrency`, the bug still slips through.
- Assuming order: calls from different tasks are not guaranteed to run in the order you made them.

Trade-off: putting logic that must be atomic into a single synchronous method (no `await`) inside the actor is the simplest fix.

## Interview Traps

### "Does an actor run on its own dedicated thread?"

**Common wrong answer:** "Yes, each actor is like a serial `DispatchQueue` with its own thread." This mental model leads to wrong assumptions about thread-locals and performance.

**Better answer:** An actor is usually not tied to any thread; its code runs on the shared cooperative thread pool and can be on different threads between `await`s. An actor only guarantees that at most one piece of its code runs at a time. The exception is `MainActor`, which is tied to the main thread. So don't use thread-local storage or check `Thread.current` to reason about actors.

### "Does an actor deadlock when its method `await`s itself or another actor?"

**Common wrong answer:** "Yes, like nested locks, if A waits for B and B waits for A, they deadlock." This is thinking carried over from locks/serial queues.

**Better answer:** Swift actors are reentrant, so they don't deadlock that way: while awaiting, the actor is released to handle other calls. The price paid is exactly the reentrancy bugs described above. Swift chose this trade-off on purpose: avoid deadlocks, but force developers not to assume state is stable across `await`.

### "If a class is marked `@MainActor`, is every method guaranteed to run on the main thread?"

**Common wrong answer:** "Guaranteed, even when an old SDK calls a delegate method from a background queue." It started out as a compile-time guarantee, not runtime magic.

**Better answer:** The compiler ensures that every call from concurrency-checked Swift code hops to the main actor. But Objective-C code or unchecked code (GCD callbacks, delegates of old frameworks) can call straight into that method from a background thread. In Swift 5 mode that silently runs on the wrong thread; Swift 6 language mode (SE-0423) adds dynamic isolation checks at boundaries with unchecked code, such as `@preconcurrency` conformances or `@objc` thunks, and crashes to expose the bug. Also, `nonisolated` methods or `@Sendable` closures inside the class still don't run on the main actor.

## Exercise

Implement an `actor RequestCounter` with `func increment()`, `func decrement()`, and `private(set) var count: Int`. Run 100 tasks concurrently (for example with `withTaskGroup`), each calling `await counter.increment()` then `await counter.decrement()`. Wait for all of them, then assert the final count is 0 (it is, because each synchronous method inside the actor is atomic).

Then deliberately introduce a reentrancy bug **inside the actor**: add `func slowIncrement() async` that reads `let current = count`, then `await Task.yield()` (or `try? await Task.sleep(for: .milliseconds(1))`), then assigns `count = current + 1`. Call it 100 times concurrently and observe that the final count is less than 100. Explain in a comment: at the `await` the actor is released, other calls read the same old value, so the writes overwrite each other (lost update). Note: merely inserting an `await` between the outside `increment()`/`decrement()` calls does not corrupt the count, because each method still runs to completion.
