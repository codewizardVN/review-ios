[English](./LargeListOptimization.md) | [Tiếng Việt](./LargeListOptimization.vi.md)

[← Performance](./README.md)

# Large List Optimization

## Root Causes of Laggy Lists

1. Cell configuration is slow (heavy computation, synchronous image decoding)
2. All cells are created at once (no lazy loading)
3. Unnecessary full-list reloads instead of diff-based updates
4. Main thread blocked during scroll

## UIKit

- `UICollectionView` / `UITableView` — cells are reused via `dequeueReusableCell`
- `UICollectionViewDiffableDataSource` — apply snapshots for animated, diffed updates
- `UICollectionViewCompositionalLayout` — flexible layouts without manual frame math
- `prefetchDataSource` — load data before cells become visible

## SwiftUI

- `List` — on iOS it's built on a UIKit collection view, so it has built-in cell reuse; prefer it over `ScrollView + ForEach` for large data
- `LazyVStack` inside `ScrollView` — only creates rows when they are about to appear, but doesn't reuse cells like UIKit/`List`, so a very long list can use more memory. A plain `VStack` in a `ScrollView` creates every row up front
- Avoid heavy computed properties in cell views
- Identify items with stable `id` to help SwiftUI diff efficiently

## Practice Questions

- If a screen scrolls poorly, what do you check first?

## Senior Take

Profile first. The fix depends on the root cause: slow cell configuration vs excessive allocations vs main thread blocking. Check Time Profiler during scroll before writing any optimization code.

## Practice Question Answers

### If a screen scrolls poorly, what do you check first?

First I reproduce it on a real device with a release build, then profile while scrolling to know exactly what the main thread is doing — no guessing and fixing. Concretely:

- Run Instruments with Animation Hitches to confirm there are hitches and whether they are commit hitches (slow main thread) or render hitches (layers too heavy).
- For commit hitches, look at Time Profiler filtered to the main thread and find the heaviest stack in `cellForItemAt`, `layoutSubviews`, or a row's `body`.

Common suspects, roughly in order of frequency:

- Synchronous image decoding or resizing in the cell.
- Creating a new `DateFormatter`/`NumberFormatter` per cell, or heavy computation (parsing, attributed strings) during configuration.
- Self-sizing cells with complex Auto Layout, constraints re-added on every reuse.
- `reloadData()` on the whole list when only one item changed.
- Render hitches from shadows without `shadowPath`, masks, blending.
- In SwiftUI: unstable identity that recreates rows, a heavy `body`, or one state change re-rendering every row. Use the SwiftUI instrument in Instruments (the new one from Xcode 26) or `Self._printChanges()` (an underscored API, for debugging only) to see which views update and why.

Only once the cause is known do you pick the fix: for images, downsample and decode in the background; for formatters, cache them; for reloads, switch to diffable snapshots. Trade-off: prefetching and caching make scrolling smoother but cost extra memory and network, so they need limits and cancellation when no longer needed.

## Interview Traps

### "Can a diffable data source use the `Hashable` model struct itself as the item identifier?"

**Common wrong answer:** Just make the model conform to `Hashable`, put it straight into the snapshot, and diffable handles the rest.

**Better answer:** If the identifier is the whole struct, when a field (e.g. `isLiked`) changes the hash changes, and diffable treats it as deleting the old item and inserting a new one: wrong animations, cells recreated, and if two items have equal values the app crashes. Use a stable ID (`Item.ID`) as the identifier, look up data from a store by ID, and when content changes call `reconfigureItems(_:)` (iOS 15+) — it updates the existing cell instead of creating a new one like `reloadItems(_:)`.

```swift
snapshot.reconfigureItems([changedID])
```

### "What's wrong with `ForEach(items, id: \.self)` or an `id` made with `UUID()`?"

**Common wrong answer:** Any `id` at all is enough for SwiftUI to diff.

**Better answer:** The `id` must be stable and unique over time. `id: \.self` with duplicate or changing values makes identity change with content; a computed `var id: UUID { UUID() }` creates a new identity on every read. The result is that SwiftUI treats every row as a new view: lost state (`@State`, scroll position), wrong animations, all rows rebuilt, janky scrolling. Use a real ID from the server or database.

### "Once `prefetchDataSource` is implemented, data is always ready when a cell appears?"

**Common wrong answer:** Prefetch is called for every cell before it's displayed, so `cellForItemAt` doesn't need to handle missing data.

**Better answer:** Prefetching is only a hint: when the user scrolls very fast, jumps to the top of the list, or on the very first display, it may not be called or may not finish in time. `cellForItemAt` must still show a placeholder and start loading itself if needed; and you must cancel work in `collectionView(_:cancelPrefetchingForItemsAt:)` so you don't waste network on cells the user has already scrolled past.

## Exercise

Build a `UICollectionView` showing 10,000 items using `UICollectionViewDiffableDataSource`. Apply a snapshot update when a filter changes. Then switch to SwiftUI and implement the same list using `List` with a stable `id`. Compare scroll performance on a real device with a release build: use Animation Hitches to measure hitches (hitch time ratio) while scrolling, and Time Profiler to see where the main thread spends its time. Note the difference between the two approaches.
