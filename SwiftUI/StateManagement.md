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

From iOS 17, with an `@Observable` class (Observation framework) the equivalent set is: `@State` to own the instance, a plain property (`let`/`var`) or `@Bindable` when you need bindings to its properties, and `.environment(model)` + `@Environment(Model.self)` instead of `EnvironmentObject`.

## What To Review

- `@State` — the view's local state (usually a value type); SwiftUI keeps the storage per view identity, so the value survives when the view struct is recreated. Declare it `private`.
- `@Binding` — a two-way (read and write) reference to state that another view owns; when the child writes to the binding, the parent's state changes.
- `@StateObject` — creates and owns an `ObservableObject`; the object is created once per identity and survives the view struct being recreated.
- `@ObservedObject` — only subscribes to an `ObservableObject` created and held elsewhere; it does not keep the object alive itself.
- `@EnvironmentObject` — reads an `ObservableObject` that an ancestor injected with `.environmentObject()`, looked up by type; a missing injection crashes at runtime.

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

Using `@ObservedObject` (as in `@ObservedObject var viewModel = FeedViewModel()`) when the view should own the object causes a new object to be created every time the view struct is re-initialized — i.e. on every parent re-render — and all its state is reset.

## Practice Questions

- When should you use `@StateObject` instead of `@ObservedObject`?
- When is `EnvironmentObject` appropriate, and when is it overuse?

## Senior Take

One-way data flow: state flows down via bindings and environment, events flow up via callbacks or view model methods. Keeping this direction consistent prevents subtle re-render bugs.

## Practice Question Answers

### When should you use `@StateObject` instead of `@ObservedObject`?

Use `@StateObject` when this view creates the object and must own it; use `@ObservedObject` when the object is created and held elsewhere and passed into the view.

The reason is that view structs are recreated very often — every parent re-render produces a new struct instance. `@StateObject` stores the object in SwiftUI-managed storage tied to the view's identity, and its initializer is an autoclosure that runs only once per identity. `@ObservedObject` is just a reference used to subscribe to `objectWillChange`; it does not keep the object alive across struct re-creations. If you write `@ObservedObject var viewModel = CartViewModel()`, every time `ShoppingCartView` is re-initialized (because its parent re-renders) you will see "CartViewModel init" logged again and all view model state reset.

Short rule: whoever creates it uses `@StateObject`, whoever receives it uses `@ObservedObject`.

From iOS 17 with `@Observable`, the equivalent pair is `@State` (owner) and a plain property or `@Bindable` (received). Trade-off: `@StateObject` only uses the first initial value, so if the view model depends on a parameter that changes over time (like `itemID`), you must handle the update yourself, e.g. via `.task(id:)` or `.id(itemID)`.

### When is `EnvironmentObject` appropriate, and when is it overuse?

`EnvironmentObject` is appropriate for dependencies that are truly shared across many levels and live for the app or scene — the logged-in session, theme, router, settings — and it is overuse when you reach for it just to avoid passing data through one or two views.

Mechanism: an ancestor calls `.environmentObject(obj)`, and any descendant with `@EnvironmentObject` looks the object up by type. Convenient, but it has three costs:

- Hidden dependencies: a view's signature doesn't tell you what it needs, and previews and tests must remember to inject the right things.
- A missing object is a runtime crash, not a compile error.
- With `ObservableObject`, any `@Published` change invalidates every view observing that object (even views that don't read the changed property), so a large "catch-all" object that changes often drags the whole view tree into re-rendering.

Signs of overuse: putting one screen's own view model into the environment, or a giant `AppState` holding everything. From iOS 17, `.environment(model)` with `@Environment(Model.self)` and `@Observable` tracks per property, which eases the performance problem, but the hidden-dependency problem remains.

## Interview Traps

### "If you pass a parameter into @StateObject via init, the view model updates when the parameter changes?"

**Common wrong answer:** Writing `_viewModel = StateObject(wrappedValue: DetailViewModel(id: id))` and believing a new view model is created when the parent passes a new `id`.

**Better answer:** The `StateObject` autoclosure is evaluated only the first time for each view identity; on later inits the new value is ignored, so the view keeps showing data for the old `id`. To recreate the view model, change identity with `.id(id)`; to keep the view model but reload data, use `.task(id: id) { await viewModel.load(id) }`.

### "With @Observable, @State var model = Model() means Model is initialized only once?"

**Common wrong answer:** Assuming `@State` with an `@Observable` class behaves exactly like `@StateObject`, so the model's initializer runs only once.

**Better answer:** SwiftUI keeps only the first instance, but the `Model()` initializer expression is still evaluated every time the view struct is re-initialized, and the extra instance is thrown away. If the model's `init` has side effects (network calls, registering observers, logging), those repeat. Keep `init` lightweight and move loading into `.task`, or create the model higher up and pass it down.

### "If you forget .environmentObject(), the compiler will catch it?"

**Common wrong answer:** Believing a missing environment object is a compile error, or that the view gets an empty default value.

**Better answer:** `@EnvironmentObject` is resolved at runtime; if no ancestor injected the object, the app crashes when the view reads it (common in previews, sheets built from UIKit, or a new screen attached to a different tree). `@Environment(Model.self)` from iOS 17 also crashes if missing, unless declared optional: `@Environment(Model.self) private var model: Model?`. That is why you inject at the root and keep previews building their full dependencies.

## Exercise

Build a parent `ShoppingCartView` that holds `@State var items: [CartItem]`. Create a child `CartItemRow` receiving a `@Binding var item: CartItem` to toggle `isSelected`. Add a `@StateObject var viewModel = CartViewModel()` in the parent. Navigate to a detail screen and back — verify `@StateObject` is NOT recreated by adding `init() { print("CartViewModel init") }` to `CartViewModel`. Explain what would happen if you used `@ObservedObject` instead.
