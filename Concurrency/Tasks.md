[English](./Tasks.md) | [Tiếng Việt](./Tasks.vi.md)

[← Concurrency](./README.md)

# Task and Cancellation

## Key Idea

`Task` is the unit of asynchronous work in Swift Concurrency. Understanding ownership and cancellation is critical for safe production code.

## What To Review

- `Task { }` — inherits actor context and priority from the calling context
- `Task.detached { }` — does not inherit context; completely independent
- `Task.cancel()` — cooperative cancellation via `Task.isCancelled`
- `withTaskCancellationHandler` — react to cancellation immediately
- `TaskGroup` — fan-out parallel work with structured lifecycle

## Example

```swift
final class FeedViewModel: ObservableObject {
    private var loadTask: Task<Void, Never>?

    func load() {
        loadTask?.cancel()
        loadTask = Task {
            await fetchFeed()
        }
    }
}
```

## Practice Questions

- If the user leaves the screen, how should an in-flight request be handled?
- What is the difference between `Task.detached` and a regular `Task`?

## Senior Take

Cancellation in Swift is cooperative — you must check `Task.isCancelled` or use `try Task.checkCancellation()` inside the task body. Cancelling a task does not stop it automatically.

## Exercise

Build a `SearchViewModel` with a `func search(query: String) async` method that cancels the previous search task before starting a new one. Use `task?.cancel()` and catch `CancellationError` in a `catch` block that prints "cancelled". Call `search(query:)` three times rapidly and confirm only the last result is applied. Explain why this pattern matters for user-facing search fields.
