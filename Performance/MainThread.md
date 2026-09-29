[English](./MainThread.md) | [Tiếng Việt](./MainThread.vi.md)

[← Performance](./README.md)

# Main Thread Discipline

## Key Idea

The main thread is responsible for all UI updates: touch handling, layout, drawing and committing frames. If code occupies the main thread for longer than one frame (about 16.7ms at 60Hz, 8.3ms at 120Hz), that frame is late and the user sees a stutter (hitch/jank); if it is blocked for roughly 250ms or more, the system treats it as a hang. So heavy non-UI work (decoding, I/O, large computations) should move off the main thread; small work does not need to — the cost of hopping threads can exceed the work itself.

## Common Violations

- Decoding JSON on the main thread after a network response (a large response can take tens of ms)
- Fetching from Core Data synchronously on the main thread (e.g. fetching thousands of objects via `viewContext`), or synchronous file reads/writes
- Decoding (decompressing) images on the main thread — UIKit decodes images lazily by default, right when the image is first displayed
- Heavy computation in `body` or `cellForItemAt` — these are called many times while scrolling or when state changes

## Detection

- Xcode: Main Thread Checker (enabled by default when running from Xcode) — note it catches *UI APIs called from a background thread*; it does not measure the main thread being blocked (see Interview Traps)
- Instruments: Time Profiler (filter to the main thread, look for long-running stacks), Hangs and Animation Hitches to see where the main thread is blocked
- Assertions in code: `dispatchPrecondition(condition: .onQueue(.main))` or `MainActor.assertIsolated()`; `Thread.isMainThread` still works in synchronous code, but in Swift 6 it cannot be called from an `async` context

## Example Fix

```swift
// Bad: decoding on main thread
func didReceiveData(_ data: Data) {
    let items = try? JSONDecoder().decode([Item].self, from: data) // blocks main
    self.items = items
}

// Good: decode off main, update on main
// (assumes the class is @MainActor and Item is Sendable)
func didReceiveData(_ data: Data) {
    Task.detached {
        let items = try? JSONDecoder().decode([Item].self, from: data)
        await MainActor.run { self.items = items }
    }
}
```

## Practice Questions

- Why must a SearchViewModel's JSON decoding and filtering move off the main thread with Task.detached, publishing the result back on @MainActor instead of doing it inline in didReceiveData?

## Senior Take

`@MainActor` on a ViewModel means its properties and methods run on the main actor (i.e. the main thread). All *synchronous* code in a `@MainActor` method — including the code between `await`s — runs on main, so heavy decoding placed there still blocks the UI. What `await` gives you is this: while the method is suspended waiting, the main actor is free to do other work (handle touches, render). Where the awaited function runs is decided by that function's own isolation: a method of another actor runs on that actor, a `@concurrent` function (or a `nonisolated async` one when `NonisolatedNonsendingByDefault` is not enabled) runs on the global concurrent executor, and `URLSession.data(for:)` waits on I/O without occupying any thread. When it finishes, the rest of the method resumes on main. So the right pattern is: keep the ViewModel `@MainActor`, push heavy CPU work into a function explicitly marked to run off main, and `await` its result.

## Practice Question Answers

### Why must a SearchViewModel's JSON decoding and filtering move off the main thread with Task.detached, publishing the result back on @MainActor instead of doing it inline in didReceiveData?

Because decoding and filtering a large response is pure CPU work that can take tens to hundreds of milliseconds, while the main thread only has about 8–16ms per frame. If `didReceiveData` does this on the main thread, the main thread is fully occupied until it finishes: no touch handling, no layout, no new frame commits — the user sees scrolling stutter or typing lag. `Task.detached` creates a task that does not inherit the caller's actor, so its body runs on the cooperative thread pool (background). Once the result is ready, we hop back to `@MainActor` to assign `items`, because state the UI reads must only change on the main thread (UIKit/SwiftUI are not thread-safe, and Swift 6 reports a compile error if isolation is violated).

```swift
func didReceiveData(_ data: Data, query: String) {
    searchTask?.cancel()
    searchTask = Task.detached(priority: .userInitiated) { [weak self] in
        let all = (try? JSONDecoder().decode([Item].self, from: data)) ?? []
        let hits = all.filter { $0.title.localizedCaseInsensitiveContains(query) }
        guard !Task.isCancelled else { return }
        await self?.apply(hits) // apply is a @MainActor method
    }
}
```

Trade-off: `Task.detached` does not inherit the parent task's priority, task-local values, or cancellation, so you must keep the handle yourself and cancel it when a new query arrives (so stale results don't overwrite fresh ones). `Item` must be `Sendable`. For small payloads (a few KB), the cost of hopping threads can exceed the work itself — measure with Time Profiler first. A cleaner alternative to `Task.detached` is moving the logic into an async function that runs off main and `await`ing it from the ViewModel. Before Swift 6.2, a `nonisolated async` function always runs on the global executor (background). From Swift 6.2, if `NonisolatedNonsendingByDefault` is enabled (the default for new projects created with Xcode 26, via the Approachable Concurrency build setting), a `nonisolated async` function runs on the caller's actor — i.e. still main when called from the ViewModel — so you must mark it `@concurrent` to be sure it runs in the background. `@concurrent` is also correct when that flag is off, so with Swift 6.2+ it is the safest way to state the intent.

## Interview Traps

### "Writing `Task { }` inside a `@MainActor` ViewModel already runs it in the background, right?"

**Common wrong answer:** Wrapping code in `Task { }` runs it on another thread, so decoding JSON inside `Task { }` won't block the UI.

**Better answer:** `Task { }` inherits the actor isolation of the context that creates it, so inside a `@MainActor` class the closure still runs on the main actor. Synchronous code inside it (decoding, filtering) still occupies the main thread; `Task` only defers it to a later turn, it does not change threads. To leave main, use `Task.detached`, or `await` a `@concurrent` function (or a `nonisolated async` one if the project has not enabled `NonisolatedNonsendingByDefault` — see the next trap).

### "The decode function is already `async`, so it definitely doesn't run on main?"

**Common wrong answer:** Marking a function `async` automatically makes it run in the background.

**Better answer:** `async` only says the function can suspend; it does not decide where it runs. An async function isolated to `@MainActor` (e.g. a ViewModel method) runs on main. For a `nonisolated async` function the behaviour depends on the version: before Swift 6.2 it runs on the global executor (background); from Swift 6.2, if `NonisolatedNonsendingByDefault` is enabled (usually via the Approachable Concurrency build setting in Xcode 26), it runs on the caller's actor — i.e. still main if called from main; if the flag is not enabled, the old behaviour stays, even on Swift 6.2. To guarantee background execution regardless of configuration, mark it `@concurrent` (Swift 6.2+). Also note: even when a function runs in the background, if its body is just long synchronous code it still occupies one cooperative-pool thread for that whole time.

### "Main Thread Checker reports nothing, so the main thread is fine?"

**Common wrong answer:** No Main Thread Checker errors means there are no performance problems on the main thread.

**Better answer:** Main Thread Checker detects the opposite direction: calling UIKit/AppKit APIs from a background thread. It does not measure the main thread being blocked for a long time. To find heavy work on main, use Instruments (Time Profiler, Hangs, Animation Hitches), Xcode's Thread Performance Checker (reports priority inversions and non-UI work on main), and hang data from Xcode Organizer/MetricKit in production.

## Exercise

You have a `SearchViewModel` that decodes a large JSON response and filters results on the main thread inside `didReceiveData`. Refactor it to decode and filter off the main thread using `Task.detached`, then publish the result back on `@MainActor`. Verify correctness with the Main Thread Checker (no warnings about UI APIs called from the background), and verify the effect with Time Profiler or Hangs in Instruments (no long decode/filter stacks left on the main thread).
