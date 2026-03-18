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

- `List` — built-in cell reuse, prefer over `ScrollView + ForEach` for large data
- `LazyVStack` inside `ScrollView` — defers creation, but no reuse
- Avoid heavy computed properties in cell views
- Identify items with stable `id` to help SwiftUI diff efficiently

## Practice Questions

- If a screen scrolls poorly, what do you check first?

## Senior Take

Profile first. The fix depends on the root cause: slow cell configuration vs excessive allocations vs main thread blocking. Check Time Profiler during scroll before writing any optimization code.

## Exercise

Build a `UICollectionView` showing 10,000 items using `UICollectionViewDiffableDataSource`. Apply a snapshot update when a filter changes. Then switch to SwiftUI and implement the same list using `List` with a stable `id`. Compare scroll performance using Time Profiler and note the difference in frame rate.
