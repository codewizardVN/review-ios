[English](./ViewLifecycle.md) | [Tiếng Việt](./ViewLifecycle.vi.md)

[← SwiftUI](./README.md)

# View Lifecycle

## Key Idea

SwiftUI views are value types (structs) that are recreated frequently. The framework diffs view descriptions and only applies real changes to the render tree — not the struct instances themselves.

## What To Review

- `onAppear` / `onDisappear` — side-effect hooks called when the view is added to / removed from the visible hierarchy. They can run many times in a view's life (popping back, switching tabs, scrolling in a lazy container), not just once like `viewDidLoad`.
- `task` modifier — the preferred way to run async work tied to a view: the task starts when the view is about to appear and is cancelled automatically when it disappears. `.task(id:)` additionally cancels and restarts the task whenever the `id` value changes.
- View identity — SwiftUI decides "is this the same view?" in two ways: structural identity (type + position in the view tree, e.g. the `if` vs `else` branch) and explicit identity (a value you assign via `.id(value)` or the IDs in a `ForEach`). State (`@State`, `@StateObject`) lives with the identity, not with the struct instance.
- When SwiftUI recreates vs reuses a view — view structs are recreated very often and that is cheap; only when identity changes does SwiftUI tear down the old view (state lost, `onDisappear` called, `.task` cancelled) and build a new one.

## Example

```swift
struct FeedView: View {
    @StateObject private var viewModel = FeedViewModel()

    var body: some View {
        List(viewModel.items) { item in
            ItemRow(item: item)
        }
        .task {
            await viewModel.load()
        }
    }
}
```

## Practice Questions

- Why is .task preferred over onAppear combined with manual task management for a CountdownView that must cancel its Task.sleep-based countdown when the user navigates away?

## Senior Take

Understanding identity is key. Across updates, a view with the same type at the same position in the hierarchy (and the same explicit ID, if any) is treated by SwiftUI as the same view, so its state is preserved even though the struct is recreated. Changing `.id()` destroys and recreates state. This matters when animating lists or resetting form fields.

## Practice Question Answers

### Why is .task preferred over onAppear combined with manual task management for a CountdownView that must cancel its Task.sleep-based countdown when the user navigates away?

`.task` is preferred because SwiftUI ties the Task's lifetime to the view's lifetime: the task starts when the view is about to appear and is cancelled automatically when the view disappears, so you never have to store or cancel it yourself.

With `onAppear`, you have to create a `Task { ... }`, store it in something like `@State var countdownTask: Task<Void, Never>?`, and remember to call `cancel()` in `onDisappear`. Forget one step, or have `onAppear` fire more than once (popping back from another screen, switching tabs), and you end up with two countdowns running in parallel or an "orphaned" task that keeps running after the user has left.

With `.task`, when the user navigates away SwiftUI cancels the task; `Task.sleep` is a cancellation checkpoint, so it throws `CancellationError` immediately and the loop ends. If you wrap it in `withTaskCancellationHandler`, the `onCancel` closure runs the moment the task is cancelled and prints "cancelled".

```swift
.task {
    await withTaskCancellationHandler {
        for value in stride(from: 10, through: 0, by: -1) {
            remaining = value
            do { try await Task.sleep(for: .seconds(1)) }
            catch { return } // cancelled when the view disappears
        }
    } onCancel: {
        print("cancelled") // runs immediately on cancellation, possibly on another thread
    }
}
```

Trade-off: cancellation is cooperative — code without an `await` point or `Task.checkCancellation()` keeps running. If you need to restart when an input changes, use `.task(id:)`. If the work must outlive the view (upload, sync), don't put it in `.task`; let a service or actor outside the view own it.

## Interview Traps

### "Is onAppear like viewDidLoad — does it run only once?"

**Common wrong answer:** Treating `onAppear` (and `.task`) like `viewDidLoad`, running exactly once in the view's life, so putting the initial data load there is safe.

**Better answer:** `onAppear` fires every time the view reappears: popping back from a detail screen, switching tabs, scrolling out and back in inside a lazy container. `.task` reruns on the same rhythm (and is cancelled every time the view disappears). So the `FeedView` in the example may call `load()` several times. If you only want to load once, guard with state in the view model (`if items.isEmpty`) or use `.task(id:)` with a value that only changes when a reload is really needed.

### "Once a task is cancelled, the code inside stops immediately, right?"

**Common wrong answer:** Assuming that when `.task` is cancelled, Swift "kills" the task and no further lines run.

**Better answer:** Cancellation in Swift Concurrency is cooperative: it only sets the `isCancelled` flag. APIs like `Task.sleep` or `URLSession` check that flag and throw `CancellationError`, but a synchronous compute loop runs to completion. Long-running code must call `try Task.checkCancellation()` or check `Task.isCancelled` itself. Also, the `.task` closure runs on the main actor (since Xcode 16 / the iOS 18 SDK, the whole `View` protocol is `@MainActor`), so heavy synchronous work inside it still blocks the UI, cancelled or not.

### "Adding .id(...) to a view just forces it to refresh the UI?"

**Common wrong answer:** Thinking `.id()` is just a way to "force a redraw" with no effect on state or side effects.

**Better answer:** Changing `.id()` changes identity: SwiftUI treats it as a brand-new view and tears down the old one — `@State`/`@StateObject` are reset, the old `.task` is cancelled, `onDisappear`/`onAppear` fire, and a new `.task` starts. That is a useful tool for resetting a form, but writing `.id(UUID())` in `body` recreates the view on every render, losing state and re-running side effects constantly.

## Exercise

Build a `CountdownView` that starts a countdown from 10 using `.task` and `try await Task.sleep`. Verify the timer cancels when navigating away by wrapping the sleep in `withTaskCancellationHandler` that prints "cancelled". Navigate away mid-countdown and confirm the message appears. Explain in a comment why `.task` is preferred over `onAppear` + manual task management for async work.
