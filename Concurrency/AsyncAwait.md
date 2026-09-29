[English](./AsyncAwait.md) | [Tiếng Việt](./AsyncAwait.vi.md)

[← Concurrency](./README.md)

# async/await

## Key Idea

`async/await` makes asynchronous code read like synchronous code, eliminating callback pyramids and making control flow easier to reason about.

## What To Review

- Marking functions with `async`: the function may suspend partway through to wait for other work, then continue.
- Calling async functions with `await`: each `await` is a potential suspension point; you can only call it from an async context (another `async` function or inside a `Task`).
- Error propagation with `async throws`: the caller writes `try await` and catches errors with `do/catch` like synchronous code, instead of passing `Error?` through a callback.
- Bridging from completion handlers **to** async using `withCheckedContinuation` / `withCheckedThrowingContinuation`: wrap an old callback API so it can be called with `await`. The opposite direction (letting old callers call async code) uses a `Task { }` inside the completion-based function.

## Example

```swift
func fetchUser(id: String) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}
```

## Practice Questions

- After rewriting a completion-handler-based fetchUser function using async/await, in what real-world scenario would you still need to keep a completion-handler version, and what do you wrap it with (and why not withCheckedThrowingContinuation for this direction)?

## Senior Take

Why `async/await` is easier to maintain than callback chains: the control flow is linear, error handling is unified via `throws`, and the compiler enforces correct usage.

## Practice Question Answers

### After rewriting a completion-handler-based fetchUser function using async/await, in what real-world scenario would you still need to keep a completion-handler version, and what do you wrap it with (and why not withCheckedThrowingContinuation for this direction)?

You still need a completion-handler API whenever a caller cannot use `async` yet: Objective-C code, older delegate- or callback-based code, or a public SDK that must keep its signature stable for existing clients. Large codebases migrate gradually, so for a while both forms of the API have to live side by side.

State one point clearly, because interviewers like to check it: `withCheckedThrowingContinuation` goes in the opposite direction. It wraps a callback API **into** `async` (for example, wrapping an old Swift function `fetchToken(completion:)`, or a delegate-based API, so it can be called with `await`; for an Objective-C method whose completion handler follows the convention, such as `LegacySessionManager.fetchToken`, the compiler already generates an `async` version), so it cannot turn an `async` function into a completion handler. To expose the new `async` version to callback-based callers, you start a `Task` inside the completion-based function:

```swift
// async -> callback direction: use a Task. In Swift 6 the closure must be @Sendable
// (and User must be Sendable) because it is carried into another Task.
func fetchUser(id: String, completion: @escaping @Sendable (Result<User, Error>) -> Void) {
    Task {
        do { completion(.success(try await fetchUser(id: id))) }
        catch { completion(.failure(error)) }
    }
}
```

The two directions often appear together: the lowest layer is old callback code wrapped with a continuation, the middle layer is written with `async`, and callback-based callers on top are served by a `Task` wrapper. For `@objc` methods on a class, the compiler generates a completion-handler variant for Objective-C automatically, so often you don't need to write the wrapper yourself.

Trade-off: the `Task` wrapper is unstructured, so callers can't cancel it unless you return or manage the `Task`, and you must decide which thread the completion is called on. Delete the wrapper once the last caller has moved to `async`.

## Interview Traps

### "Does `await` block the current thread?"

**Common wrong answer:** "Yes, `await` waits like `DispatchSemaphore.wait()`, so don't call it on the main thread." This confuses suspending with blocking.

**Better answer:** `await` is a suspension point: the current task pauses and gives the thread back to the executor to run other work, so the main thread keeps handling UI while `URLSession` waits on the network. When the result arrives the task resumes, possibly on a different thread (unless it is isolated to `@MainActor`). What really blocks a thread is heavy synchronous code between two `await`s, or using a semaphore to wait for async work, which can deadlock the cooperative thread pool.

### "What if a continuation is never resumed, or is resumed twice?"

**Common wrong answer:** "No problem, a second callback is just ignored, and a missing one acts like a timeout." Swift has no such automatic ignore or timeout.

**Better answer:** A continuation must be resumed exactly once. With `withCheckedThrowingContinuation`, a second resume crashes at runtime; never resuming leaves the task suspended forever, and the runtime logs "SWIFT TASK CONTINUATION MISUSE" when the continuation is deallocated. The `withUnsafe...` variants skip these checks, so the bugs are quieter. That's why every branch of the old callback (including `guard ... else { return }` branches) must call `resume`.

### "Does an `async` function automatically run on a background thread?"

**Common wrong answer:** "Yes, marking it `async` moves the code off the main thread, so heavy JSON decoding is fine." `async` only says the function can suspend, not where it runs.

**Better answer:** Where it runs is decided by isolation. A function isolated to `@MainActor` (marked directly, or a method of a `@MainActor` type) runs its synchronous parts on the main thread, so heavy `JSONDecoder().decode` there still janks the UI. The behaviour of a `nonisolated async` function depends on the version and settings: since Swift 5.7 (SE-0338) it always hops to the global executor (i.e. leaves the main thread). From Swift 6.2 (SE-0461), if you enable the upcoming feature `NonisolatedNonsendingByDefault` (part of Xcode 26's "Approachable Concurrency" setting), it runs on the caller's actor by default; you then mark it `@concurrent` when you really want it off the actor. Without that feature, Swift 6.2 keeps the old behaviour.

## Exercise

Rewrite this completion-handler function using async/await:

```swift
func fetchUser(id: String, completion: @escaping (Result<User, Error>) -> Void)
```

Then do the two bridging jobs in the correct direction:

1. Assume the lower layer is an old callback API written in Swift, for example `func fetchToken(completion: @escaping (String?, Error?) -> Void)`. Use `withCheckedThrowingContinuation` to wrap it into `func fetchToken() async throws -> String`, and make sure every branch calls `resume` exactly once.
2. Provide a completion-handler version of `fetchUser` again for old callers by calling the async version inside `Task { }`. Write a comment explaining in what real-world scenario this wrapper is still needed (hint: delegate-based or callback-based callers, Objective-C code, a public SDK that must keep its signature).
