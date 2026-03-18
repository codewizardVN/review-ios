[English](./MainThread.md) | [Tiếng Việt](./MainThread.vi.md)

[← Performance](./README.md)

# Main Thread Discipline

## Key Idea

The main thread is responsible for all UI updates. Blocking it causes dropped frames (jank). Work that does not touch UI must happen off the main thread.

## Common Violations

- Decoding JSON on the main thread after a network response
- Fetching from Core Data synchronously on the main thread
- Image decompression on the main thread
- Heavy computation triggered in `body` or `cellForItemAt`

## Detection

- Xcode: Main Thread Checker (enabled by default in debug)
- Instruments: Time Profiler — look for long main-thread frames
- `Thread.isMainThread` assertions in critical paths

## Example Fix

```swift
// Bad: decoding on main thread
func didReceiveData(_ data: Data) {
    let items = try? JSONDecoder().decode([Item].self, from: data) // blocks main
    self.items = items
}

// Good: decode off main, update on main
func didReceiveData(_ data: Data) {
    Task.detached {
        let items = try? JSONDecoder().decode([Item].self, from: data)
        await MainActor.run { self.items = items }
    }
}
```

## Senior Take

`@MainActor` on ViewModels does not mean all work runs on the main thread — it means properties and methods are accessed on the main thread. Async work inside a `@MainActor` function suspends to a background thread when awaiting, which is correct behavior.

## Exercise

You have a `SearchViewModel` that decodes a large JSON response and filters results on the main thread inside `didReceiveData`. Refactor it to decode and filter off the main thread using `Task.detached`, then publish the result back on `@MainActor`. Verify correctness with the Main Thread Checker.
