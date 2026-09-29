[English](./Tasks.md) | [Tiếng Việt](./Tasks.vi.md)

[← Concurrency](./README.md)

# Task and Cancellation

## Key Idea

`Task` is the unit of asynchronous work in Swift Concurrency. Understanding ownership and cancellation is critical for safe production code.

## What To Review

- `Task { }` — creates an unstructured task that inherits actor isolation, priority and task-local values from where it is created (created in `@MainActor` code, the body runs on the main actor).
- `Task.detached { }` — also an unstructured task, but inherits no actor, priority or task-locals; the body runs on the global executor unless you `await` into an actor yourself.
- `Task.cancel()` — cancellation is cooperative: it only sets a flag, and the code inside must check `Task.isCancelled` or call `try Task.checkCancellation()` (which throws `CancellationError`).
- `withTaskCancellationHandler` — registers a closure that is called right when the task is cancelled (possibly concurrently with the main work), used to tear down external resources such as a socket or an old callback-based request.
- `TaskGroup` — fans out several child tasks in parallel; the group only finishes when every child is done, and cancelling the group cancels all children (structured lifecycle).

## Example

```swift
@MainActor
final class FeedViewModel: ObservableObject {
    private var loadTask: Task<Void, Never>?

    func load() {
        loadTask?.cancel()          // cancel the previous load (if still running)
        loadTask = Task {
            await fetchFeed()
        }
    }

    func cancel() {
        loadTask?.cancel()
    }

    private func fetchFeed() async { /* call the API, update @Published */ }
}
```

## Practice Questions

- If the user leaves the screen, how should an in-flight request be handled?
- What is the difference between `Task.detached` and a regular `Task`?

## Senior Take

Cancellation in Swift is cooperative — you must check `Task.isCancelled` or use `try Task.checkCancellation()` inside the task body. Cancelling a task does not stop it automatically.

## Practice Question Answers

### If the user leaves the screen, how should an in-flight request be handled?

The request should be cancelled, because nobody will see the result, and letting it run only wastes battery and bandwidth, or even causes bugs when it updates a screen that is already gone.

Concretely: in SwiftUI the cleanest way is the `.task { await viewModel.load() }` modifier. That task is tied to the view's lifetime and is cancelled automatically when the view disappears. In UIKit, or with the `FeedViewModel` in the example, the view model keeps `loadTask` and exposes a `cancel()` method; the view controller calls it in `viewDidDisappear` (calling it in `deinit` only helps if the task doesn't hold `self` strongly, because otherwise `deinit` won't run until the task finishes). Cancelling only sets a flag; the code inside has to react to it. Fortunately, system APIs such as `URLSession.data(from:)` and `Task.sleep` already check for cancellation and throw. In loops you write yourself, call `try Task.checkCancellation()`.

```swift
override func viewDidDisappear(_ animated: Bool) {
    super.viewDidDisappear(animated)
    viewModel.cancel()
}
```

Trade-off: not every request should be cancelled. A write such as "send message" or "pay" should complete even if the user leaves the screen. That work should belong to a service that outlives the screen (or a background `URLSession`), not to the screen's view model.

### What is the difference between `Task.detached` and a regular `Task`?

`Task { }` inherits the context of the place that creates it, while `Task.detached { }` inherits nothing.

"Context" here means three things: actor isolation (created inside a `@MainActor` view model, the body runs on the main actor), priority, and task-local values. What they share: both are unstructured tasks, meaning neither is cancelled automatically when the scope that created it ends, and you must keep the handle yourself to cancel it.

Because `Task { }` inside `@MainActor` runs on the main thread, many people use `Task.detached` to "push heavy work to the background". It works, but it's usually not the best choice: you lose priority and task-locals (for example tracing context), and the closure must be `@Sendable`, which makes capturing state awkward. A clearer approach is to move the heavy work into a `nonisolated async` function or into a dedicated `actor`, and `await` it from a regular `Task`. Mind the version: a `nonisolated async` function runs on the global executor by default (Swift 5.7+); but if the project enables Swift 6.2's upcoming feature `NonisolatedNonsendingByDefault` (included in Xcode 26's "Approachable Concurrency" setting), it runs on the caller's actor, and you then need `@concurrent` to really leave the main actor. A synchronous (non-`async`) `nonisolated` function always runs right on the caller's thread.

Use `Task.detached` when you really want to cut ties with the current context, for example low-priority cleanup that must not run on the main actor. Otherwise, default to `Task { }` or structured concurrency.

## Interview Traps

### "Calling `task.cancel()` stops the task immediately, right?"

**Common wrong answer:** "Yes, cancel kills the task like killing a thread." Swift has no forced stop for tasks.

**Better answer:** Cancellation is cooperative: `cancel()` only sets the `isCancelled` flag and propagates it to child tasks. The task keeps running until its code checks the flag (`Task.isCancelled`, `try Task.checkCancellation()`) or calls an API that checks it. A synchronous compute loop with no checks runs to completion even after being cancelled. To react immediately (for example closing a socket), use `withTaskCancellationHandler`.

### "In `SearchViewModel`, is catching `CancellationError` enough to detect a cancelled request?"

**Common wrong answer:** "Yes, everything that's cancelled throws `CancellationError`." This is a very common wrong assumption in the search exercise.

**Better answer:** When cancelled, `URLSession` throws a `URLError` with code `.cancelled`, not `CancellationError`. If you only `catch is CancellationError`, a cancelled request falls into the generic error branch and the UI may show "Something went wrong" on every keystroke. Check both, or more simply check `Task.isCancelled` inside `catch` before showing an error.

```swift
catch where Task.isCancelled { print("cancelled") }
```

### "Does `[weak self]` in `Task { }` prevent a retain cycle?"

**Common wrong answer:** "You always need `[weak self]` and then `guard let self` on the first line, like with regular closures." Written that way, it usually solves nothing.

**Better answer:** A `Task` holds its closure until it finishes, so capturing `self` strongly only extends `self`'s lifetime until the task ends; it is not a permanent cycle. And `guard let self` at the top of the task turns `self` into a strong reference for the task's whole run, so the `weak` is almost pointless. The real problem is a task that never ends (for example `for await` over a stream that never finishes): if that task holds `self` strongly, `deinit` never runs, so you must cancel it from outside (`onDisappear`, `viewDidDisappear`), or capture `weak` and only unwrap `self` briefly inside each iteration.

## Exercise

Build a `SearchViewModel` with a `func search(query: String)` method that cancels the previous search task before starting a new one (keep the task in a `task` property, call `task?.cancel()`, then create a new `Task { }`). In `catch`, detect the cancelled case and print "cancelled" instead of showing an error; note that `URLSession` throws `URLError(.cancelled)`, not `CancellationError`, so use `catch where Task.isCancelled` or check both (see Interview Traps). Call `search(query:)` three times rapidly and confirm only the last result is applied. Explain why this pattern matters for user-facing search fields.
