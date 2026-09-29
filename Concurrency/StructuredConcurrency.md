[English](./StructuredConcurrency.md) | [Tiếng Việt](./StructuredConcurrency.vi.md)

[← Concurrency](./README.md)

# Structured Concurrency

## Key Idea

Structured concurrency ties the lifetime of child tasks to their parent scope: the scope can only exit once every child task has finished, so no child outlives the place that created it. When the parent is cancelled, cancellation propagates to every child automatically; when the scope exits because of an error (or with an `async let` that was never awaited), the still-running children are cancelled and then awaited before exiting.

## What To Review

- `async let` — creates a child task that starts right at the declaration line, running alongside the code after it; you `await` the variable when you need the result. Fits a fixed number of jobs.
- `withTaskGroup` / `withThrowingTaskGroup` — dynamic fan-out: add as many children as you like with `group.addTask` (for example in a loop), then read results in completion order.
- Task hierarchy — child tasks belong to the parent: cancelling the parent cancels every child, and the parent cannot finish before its children.
- Task priority propagation — child tasks inherit the parent's priority; if a high-priority task is waiting on the result of a lower-priority task, the runtime can raise its priority (priority escalation) to avoid priority inversion.

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

## Practice Question Answers

### When is async let clearer for a loadProfile() function that fetches user, posts, and followers concurrently, and when does withThrowingTaskGroup become necessary instead?

`async let` is clearer when the amount of work is fixed and known when you write the code, and each piece returns a different type; `withThrowingTaskGroup` becomes necessary when the number of tasks is only known at runtime, or when you need to handle results in completion order.

For `loadProfile()`, the three requests `user`, `posts`, `followers` are fixed and have different types (`User`, `[Post]`, `[User]`), so `async let` reads almost like sequential code and keeps each variable's type:

```swift
func loadProfile() async throws -> Profile {
    async let user = fetchUser()
    async let posts = fetchPosts()
    async let followers = fetchFollowers()
    return try await Profile(user: user, posts: posts, followers: followers)
}
```

A task group forces every child to return the same type (`of: Item.self`), so using a group for three different types means wrapping them in an enum and switching back, which is long and error-prone. But a group wins when:
- The list of requests is a dynamic array (like `fetchAll(ids:)` in the example, or sections toggled by feature flags).
- You want to limit how many requests run at once (only add a new task when an old one finishes).
- You want to show results one by one, or stop early at the first result.

Both are structured: the function only returns after every child has finished, and when one child's error propagates out of the scope, the remaining children are cancelled. Note that the error only propagates when you `await` that particular child (with `async let`) or read results from the group (see the trap below). With `async let`, the variables are awaited in the order they appear in the expression, so if `posts` fails early but `user` is slow, the error is only thrown after `user` finishes.

## Interview Traps

### "When does an `async let` start running? What if you never `await` it?"

**Common wrong answer:** "It runs when you `await` it, and if you never `await` it, it keeps running in the background like `Task { }`." Both halves are wrong.

**Better answer:** An `async let` child task starts right at the declaration line; `await` is only where you collect the result. If the scope ends without awaiting it, Swift cancels that child automatically and still waits for it to finish before leaving the scope, so no task "leaks" out. Consequence: a forgotten `async let` doesn't leave a request running in the background, but the function may still have to wait for it to stop.

### "In `withThrowingTaskGroup`, when one child throws, are the other children cancelled immediately?"

**Common wrong answer:** "Yes, the first error always stops the whole group." That's only true if you actually read results from the group.

**Better answer:** A child's error is only rethrown when you collect results via `next()`, `for try await`, or `reduce` as in `fetchAll`. Only when the error escapes the group body are the remaining children cancelled. If the body never reads results, the group implicitly waits for all children to finish and their errors are discarded. If you just need to run work without results, `withThrowingDiscardingTaskGroup` (iOS 17+) cancels the whole group as soon as one child throws.

### "Does `fetchAll(ids:)` return items in the same order as `ids`?"

**Common wrong answer:** "Yes, because tasks are added in loop order." The order tasks are added is not the order results arrive.

**Better answer:** A group yields results in the order children complete, so `reduce(into: [])` builds the array in whichever order the requests came back. If the UI needs to keep the order, return an index or id from the child and sort afterwards, or collect into a dictionary.

```swift
try await withThrowingTaskGroup(of: (Int, Item).self) { group in
    for (index, id) in ids.enumerated() {
        group.addTask { (index, try await fetchItem(id: id)) }
    }
    var result = [(Int, Item)]()
    for try await pair in group { result.append(pair) }
    return result.sorted { $0.0 < $1.0 }.map { $0.1 }
}
```

## Exercise

Write a `loadProfile() async throws -> Profile` function that fetches `user`, `posts`, and `followers` concurrently using `async let`. Then rewrite the same function using `withThrowingTaskGroup` so the set of requests can be driven by a dynamic array. Write a comment comparing the two: when is `async let` clearer, and when does `TaskGroup` become necessary?
