[English](./CollectionViewDiffable.md) | [Tiếng Việt](./CollectionViewDiffable.vi.md)

[← UIKit and App Lifecycle](./README.md)

# Collection View and Diffable Data Source

## Key Idea

`UICollectionViewDiffableDataSource` makes list updates easier to reason about by describing state snapshots instead of manually calculating insertions and deletions.

## What To Review

- Stable item identity: the item identifier is the `Hashable` value diffable uses to recognize "this is still the same item". It should be an ID that does not change over time (for example the server ID), not all of the displayed data.
- Snapshot application cost: on every `apply`, diffable compares the old and new snapshots to compute inserts/deletes/moves, then updates the collection view. The larger the list and the more often you apply, the more it costs.
- Cell reuse and configuration: cells are reused while scrolling, so every configuration must reset all visible state. The modern approach is `UICollectionView.CellRegistration` (iOS 14+) together with content configurations such as `UIListContentConfiguration`.
- Section modeling: section identifiers must also be `Hashable` and unique, usually an enum (for example `.unread`, `.read`). Per-section layout usually goes with `UICollectionViewCompositionalLayout`.

## Practice Questions

- Why can diffable still feel slow on large lists?
- What breaks if item identifiers are not stable?

## Senior Take

Diffable data source improves correctness, not magic performance. You still need good item identity, careful snapshot frequency, and lightweight cell configuration.

## Practice Question Answers

### Why can diffable still feel slow on large lists?

Diffable is slow on large lists because every `apply` has to compare the entire old snapshot with the new one, and both that work and cell configuration cost time on the main thread. Diffable only saves you from computing inserts/deletes yourself; it does not make the computation disappear.

Common causes:

- **Heavy identifiers.** If a whole model struct is the item identifier, every diff must hash and compare every field of thousands of items. Small IDs (`UUID`, `Int`, `String`) are much faster.
- **Applying too often.** For example, one apply per incoming WebSocket message. Batch changes (debounce) and apply once.
- **Animating huge changes.** Animating thousands of inserts/deletes at once is expensive. When the data changes completely (a filter change, say), use `applySnapshotUsingReloadData(_:)` (iOS 15+) to skip the diff.
- **Reloading instead of reconfiguring.** `reloadItems` throws away the old cell and dequeues a new one. `reconfigureItems` (iOS 15+) updates content on the existing cell, which is much cheaper.
- **Heavy cell configuration.** Decoding images, formatting dates, or building attributed text inside the cell provider.

A version detail: since iOS 15, `apply(_:animatingDifferences: false)` still diffs, it just does not animate. Before iOS 15 it was equivalent to `reloadData`. Trade-off: Apple's older documentation allowed calling `apply` from a background queue as long as you always use the same queue (mixing main and background leads to unpredictable bugs). But in the current SDK the diffable data source is a UIKit class marked `@MainActor`, so with Swift 6 apply on the main actor, and if needed move only the heavy data preparation off the main thread.

### What breaks if item identifiers are not stable?

If identifiers are not stable, diffable treats every change as "delete the old item, insert a new one", so animations, selection, cell state, and scroll position all break. Diffable identifies items only through `Hashable`. If the identifier changes every time you build a snapshot, for example a fresh `UUID()` generated each time you map from the API, or a whole struct that includes an `isRead` field, then to diffable it is a completely different item.

Concrete consequences:

- Cells flash or fade out/in instead of updating in place.
- Selection and focus are lost, and text fields inside cells are reset.
- `reloadItems`/`reconfigureItems` cannot be used because the old identifier is no longer in the snapshot.
- If two items share an identifier in the same snapshot, the app hits an exception (crash) when the snapshot is built or applied.

For the notifications exercise, the identifier should be the server ID of the app's notification model (for example `AppNotification.ID`, named differently to avoid confusion with `Foundation.Notification`), without `isRead`. Content is looked up from a store by ID. When marking as read:

```swift
var snapshot = dataSource.snapshot()
snapshot.deleteItems([id])
snapshot.appendItems([id], toSection: .read)
dataSource.apply(snapshot, animatingDifferences: true)
```

Because the ID does not change, diffable understands this as a move, not a deletion plus an unrelated insertion. Note: a move only changes position; it does not call the cell provider again. If the cell must change its appearance (for example removing the "unread" dot), update the store first and then call `reconfigureItems([id])` so the cell reads the new data. Trade-off: if moving between the two sections is still visually confusing, keep the item where it is with a "read" style and only reorder when the user leaves the screen.

## Interview Traps

### "Is it fine to use the model struct itself as the item identifier for convenience?"

**Common wrong answer:** Sure, the struct is already `Hashable`, so diffable will figure out which item changed and update it.

**Better answer:** Diffable has no notion of "same item, different content". It only knows whether two hashes are equal. Change one field like `isRead` and the hash changes, so the old item is deleted and a new one inserted, the cell flashes and loses state. Apple recommends using a stable ID as the identifier, and calling `snapshot.reconfigureItems([id])` when content changes. Using the whole struct is only fine for data that practically never changes.

### "What is the difference between reloadItems and reconfigureItems?"

**Common wrong answer:** They are the same; both make the cell display the new data.

**Better answer:** `reloadItems` discards the current cell and dequeues a new one through the cell provider, so it can flash, lose state like text being typed, and costs more. `reconfigureItems` (iOS 15+) calls the cell provider again on the cell that is already on screen, keeping the same cell, which is lighter and smoother. Only use `reloadItems` when you need to switch to a different cell type.

### "Duplicate item identifiers in two different sections are okay, right?"

**Common wrong answer:** Yes, because each section is its own list.

**Better answer:** Identifiers must be unique across the **entire** snapshot, not just within a section. Duplicates cause an exception (crash) when the snapshot is built or applied, with an error message about duplicate identifiers. If the same data must appear in two sections (for example "Pinned" and "All"), wrap it in an enum such as `case pinned(ID)` and `case all(ID)` so the two values differ.

## Exercise

Design a two-section collection view for notifications: `unread` and `read`. Define the item identifier and explain how you would update one item from unread to read without causing confusing animations.
