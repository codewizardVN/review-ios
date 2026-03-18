[English](./StateManagement.md) | [Tiếng Việt](./StateManagement.vi.md)

[← SwiftUI](./README.md)

# State Management

## Property Wrappers at a Glance

| Wrapper | Owns the state? | Source |
|---|---|---|
| `@State` | Yes | Local to this view |
| `@Binding` | No | Passed in from parent |
| `@StateObject` | Yes | Owns the object lifetime |
| `@ObservedObject` | No | Object owned elsewhere |
| `@EnvironmentObject` | No | Injected from ancestor |

## What To Review

- `@State` — simple local value state; SwiftUI owns it
- `@Binding` — two-way reference to state owned by a parent
- `@StateObject` — creates and owns an `ObservableObject`; survives view re-creation
- `@ObservedObject` — subscribes to an `ObservableObject` owned by someone else
- `@EnvironmentObject` — global-ish object injected via `.environmentObject()`

## Key Distinction: `@StateObject` vs `@ObservedObject`

```swift
// Correct: this view owns the view model
struct FeedView: View {
    @StateObject private var viewModel = FeedViewModel()
}

// Correct: parent created it, this view just observes
struct FeedView: View {
    @ObservedObject var viewModel: FeedViewModel
}
```

Using `@ObservedObject` when the view should own the object causes the object to be recreated on every parent re-render.

## Practice Questions

- When should you use `@StateObject` instead of `@ObservedObject`?
- When is `EnvironmentObject` appropriate, and when is it overuse?

## Senior Take

One-way data flow: state flows down via bindings and environment, events flow up via callbacks or view model methods. Keeping this direction consistent prevents subtle re-render bugs.

## Exercise

Build a parent `ShoppingCartView` that holds `@State var items: [CartItem]`. Create a child `CartItemRow` receiving a `@Binding<CartItem>` to toggle `isSelected`. Add a `@StateObject var viewModel = CartViewModel()` in the parent. Navigate to a detail screen and back — verify `@StateObject` is NOT recreated by adding `init() { print("CartViewModel init") }`. Explain what would happen if you used `@ObservedObject` instead.
