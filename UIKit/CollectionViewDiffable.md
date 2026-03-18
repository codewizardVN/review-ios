[English](./CollectionViewDiffable.md) | [Tiếng Việt](./CollectionViewDiffable.vi.md)

[← UIKit and App Lifecycle](./README.md)

# Collection View and Diffable Data Source

## Key Idea

`UICollectionViewDiffableDataSource` makes list updates easier to reason about by describing state snapshots instead of manually calculating insertions and deletions.

## What To Review

- Stable item identity
- Snapshot application cost
- Cell reuse and configuration
- Section modeling

## Practice Questions

- Why can diffable still feel slow on large lists?
- What breaks if item identifiers are not stable?

## Senior Take

Diffable data source improves correctness, not magic performance. You still need good item identity, careful snapshot frequency, and lightweight cell configuration.

## Exercise

Design a two-section collection view for notifications: `unread` and `read`. Define the item identifier and explain how you would update one item from unread to read without causing confusing animations.
