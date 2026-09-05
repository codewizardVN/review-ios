[English](./ViewLifecycle.md) | [Tiếng Việt](./ViewLifecycle.vi.md)

[← SwiftUI](./README.md)

# View Lifecycle

## Key Idea

SwiftUI views are value types (structs) that are recreated frequently. The framework diffs view descriptions and only applies real changes to the render tree — not the struct instances themselves.

## What To Review

- `onAppear` / `onDisappear` — side effect hooks tied to view visibility
- `task` modifier — preferred for async work; auto-cancels when view disappears
- View identity — structural vs explicit identity (`.id(value)`)
- When SwiftUI decides to recreate vs reuse a view

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

Understanding identity is key. Two views with the same type at the same position in the hierarchy share state. Changing `.id()` destroys and recreates state. This matters when animating lists or resetting form fields.

## Exercise

Build a `CountdownView` that starts a countdown from 10 using `.task` and `try await Task.sleep`. Verify the timer cancels when navigating away by wrapping the sleep in `withTaskCancellationHandler` that prints "cancelled". Navigate away mid-countdown and confirm the message appears. Explain in a comment why `.task` is preferred over `onAppear` + manual task management for async work.
