[English](./RenderingPerformance.md) | [Tiếng Việt](./RenderingPerformance.vi.md)

[← SwiftUI](./README.md)

# Rendering Performance

## Common Causes of Unnecessary Re-renders

- `@ObservedObject` / `@StateObject` publishing changes for properties the view does not actually use — with `ObservableObject`, any `@Published` change re-evaluates `body` for every view observing the object
- Large `@EnvironmentObject` updating frequently — every view reading that object, at any level, gets invalidated
- Expensive computations in `body` — sorting/filtering, creating formatters, decoding images re-run on every `body` call, on the main thread
- Missing `Equatable` conformance on view types that could use `.equatable()` — when a view's inputs contain things SwiftUI can't compare on its own (closures, reference types), SwiftUI treats them as changed

## What To Review

- `equatable()` modifier — for a view conforming to `Equatable`, `.equatable()` (which wraps the view in `EquatableView`) makes SwiftUI use your `==` to decide whether `body` needs re-evaluating; if `==` returns `true`, it is skipped. Only useful when SwiftUI's default comparison isn't enough.
- Splitting views — each child view is its own invalidation boundary; a small view that receives only the data it needs (narrow observation scope) doesn't re-run `body` when other data changes.
- `LazyVStack` / `LazyHStack` — create child views only when they are about to appear on screen instead of all up front; but they don't recycle views already created.
- `List` vs `ScrollView + LazyVStack` — `List` is built on UIKit's `UICollectionView` (iOS 16+; `UITableView` before that) so it has cell reuse built in; `LazyVStack` is more flexible for layout but doesn't reuse.

## Practice Questions

- Why does a view keep reloading unexpectedly?
- If a large list is laggy, where do you start debugging?

## Senior Take

The first question is always: which `@Published` property changed and which views observed it? (With `@Observable`, the equivalent question is: which property read in `body` just changed.) Use the SwiftUI template in Instruments — from Xcode 26 there is a new SwiftUI instrument that shows long `body` updates and a Cause & Effect graph — or add `let _ = Self._printChanges()` in `body` to trace re-renders during debugging.

## Practice Question Answers

### Why does a view keep reloading unexpectedly?

Usually because the view depends on a data source broader than what it actually uses, so every small change in that source forces its `body` to be re-evaluated.

Common causes:

- `ObservableObject`: any `@Published` change fires `objectWillChange`, and every view observing the object is invalidated, even if it doesn't read the property that changed. That is exactly why `selectedTab` in the exercise makes every row re-render.
- A parent re-render recreates the child struct; if the child's inputs can't be compared (closures, a new reference-type instance), SwiftUI treats them as "changed" and runs the child's `body` again.
- Unstable identity: `.id(UUID())`, `ForEach(..., id: \.self)` with changing values, causing views to be destroyed and recreated rather than just updated.
- An environment value changing higher up (for example a large environment object).

How to find it: add `let _ = Self._printChanges()` in `body` to see which property triggered the re-render (an underscored API, debug only). How to fix it: split into smaller views and pass only the values each view needs, move to `@Observable` (iOS 17+) for per-property tracking. Note: `body` running again does not mean pixels are redrawn; only optimize when it causes a real problem.

### If a large list is laggy, where do you start debugging?

Start by measuring, not guessing: profile on a real device, in a Release build, with Instruments (the SwiftUI template, Time Profiler, Hitches/Animation Hitches) to learn why frames are late.

Then check in this order:

1. Container: are you using a `VStack` or `ScrollView` + plain `VStack` with thousands of elements? Switch to `List` or `LazyVStack`.
2. Work in the row's `body`: creating a `DateFormatter`, sorting/filtering arrays, decoding images on the main thread. Move this into the model or a cache.
3. Identity: `ForEach` must use stable IDs (`Identifiable`); using indices or a changing `.id()` makes the list rebuild every row.
4. Observation scope: is each row observing the whole view model? Pass a `User` (value) into the row instead of the whole `viewModel`.
5. Images: load asynchronously and downsample to the displayed size.

Trade-off: `List` (built on UIKit's collection view) reuses cells and is usually smoother with very large data, while `LazyVStack` is more flexible for layout but keeps created views around. Don't sprinkle `.equatable()` everywhere before you have measured a benefit.

## Interview Traps

### "LazyVStack reuses views just like List/UITableView?"

**Common wrong answer:** Assuming `LazyVStack` recycles rows like `UITableView`, so swapping it in for `List` gives equivalent performance with tens of thousands of items.

**Better answer:** `LazyVStack` only defers creating views until they are needed on screen; it does not recycle. Rows that were created are generally kept as you scroll past, so memory grows as the user scrolls deeper. `List` is built on UIKit's collection view and reuses cells, so for very long, uniform lists `List` is usually the safer choice.

### "Switching to @Observable eliminates redundant re-renders?"

**Common wrong answer:** Thinking `@Observable` optimizes everything automatically, so you no longer need to care how views read data.

**Better answer:** `@Observable` only tracks the properties read in `body`, which is a big improvement over `ObservableObject`. But if `body` reads the whole `users` array and passes each element to a row, changing one element still invalidates the view reading that array; and if a row receives the whole `viewModel` and reads `viewModel.selectedTab`, the row still depends on the tab. Tracking is only narrow when your reads are narrow.

### "body being called again means the view is redrawn, which is expensive?"

**Common wrong answer:** Treating every `body` call as a full-screen render, so the goal is to never let `body` run again.

**Better answer:** `body` only produces a lightweight view description; SwiftUI diffs the new description against the old one and updates only the parts of the render tree that actually differ. The real cost comes from heavy work inside `body` and from recreating identity. So the good answer is: keep `body` cheap and pure, measure with Instruments, and only optimize the number of `body` calls when it shows up in the profile.

## Exercise

Create a `UserListView` with `@StateObject var viewModel` (an `ObservableObject`) that has `@Published var users: [User]` and `@Published var selectedTab: Int`. Write a row view that receives the whole view model (`@ObservedObject var viewModel`) together with the user to display, and add `let _ = Self._printChanges()` to the row's `body`. Change `selectedTab` and observe that every row re-renders unnecessarily. Fix it by having the row receive only the value it needs (`let user: User`) instead of the whole view model, so the row's observation scope is narrow. Confirm rows no longer re-render on tab change (`UserListView` itself still re-renders, because it observes the view model — that is expected).
