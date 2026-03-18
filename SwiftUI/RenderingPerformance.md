[English](./RenderingPerformance.md) | [Tiếng Việt](./RenderingPerformance.vi.md)

[← SwiftUI](./README.md)

# Rendering Performance

## Common Causes of Unnecessary Re-renders

- `@ObservedObject` / `@StateObject` publishing changes for properties the view does not actually use
- Large `@EnvironmentObject` updating frequently
- Expensive computations in `body`
- Missing `Equatable` conformance on view types that could use `.equatable()`

## What To Review

- `equatable()` modifier — skip re-render if input has not changed
- Splitting views — smaller views with narrower observation scope re-render less
- `LazyVStack` / `LazyHStack` — defer creation of off-screen views
- `List` vs `ScrollView + LazyVStack` — `List` has built-in cell reuse

## Practice Questions

- Why does a view keep reloading unexpectedly?
- If a large list is laggy, where do you start debugging?

## Senior Take

The first question is always: which `@Published` property changed and which views observed it? Use Xcode's SwiftUI rendering instrumentation or add `let _ = Self._printChanges()` in `body` to trace re-renders during debugging.

## Exercise

Create a `UserListView` with `@StateObject var viewModel` that publishes `var users: [User]` and `var selectedTab: Int`. Add `Self._printChanges()` to a row view body. Change `selectedTab` and observe that every row re-renders unnecessarily. Fix it by extracting the row into a separate view with narrower observation scope. Confirm rows no longer re-render on tab change.
