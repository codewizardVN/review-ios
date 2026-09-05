[English](./AsyncAwait.md) | [Tiếng Việt](./AsyncAwait.vi.md)

[← Concurrency](./README.md)

# async/await

## Key Idea

`async/await` makes asynchronous code read like synchronous code, eliminating callback pyramids and making control flow easier to reason about.

## What To Review

- Marking functions with `async`
- Calling async functions with `await`
- Error propagation with `async throws`
- Bridging from completion handlers using `withCheckedContinuation` / `withCheckedThrowingContinuation`

## Example

```swift
func fetchUser(id: String) async throws -> User {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}
```

## Practice Questions

- After rewriting a completion-handler-based fetchUser function using async/await, in what real-world scenario would you still need to wrap it back into a completion-handler API with withCheckedThrowingContinuation?

## Senior Take

Why `async/await` is easier to maintain than callback chains: the control flow is linear, error handling is unified via `throws`, and the compiler enforces correct usage.

## Exercise

Rewrite this completion-handler function using async/await:

```swift
func fetchUser(id: String, completion: @escaping (Result<User, Error>) -> Void)
```

Then wrap the new async version back into a completion-handler API using `withCheckedThrowingContinuation`. Write a comment explaining in what real-world scenario the wrapper is still needed (hint: delegate-based or callback-based callers).
