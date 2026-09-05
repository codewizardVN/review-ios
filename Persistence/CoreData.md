[English](./CoreData.md) | [Tiếng Việt](./CoreData.vi.md)

[← Persistence](./README.md)

# Core Data

## Key Idea

Core Data is an object graph and persistence framework, not just a database wrapper. `NSManagedObjectContext` tracks changes; `NSPersistentContainer` owns the stack and the underlying SQLite store.

## What To Review

- `NSManagedObjectContext` — main context (UI) vs background context (writes/imports), never share a context across threads
- `NSPersistentContainer` / `NSPersistentCloudKitContainer` — stack setup, `newBackgroundContext()`
- Merge policies — `NSMergeByPropertyObjectTrumpMergePolicy` vs `NSMergeByPropertyStoreTrumpMergePolicy` for resolving conflicts between contexts
- Lightweight vs manual migrations — when the automatic mapping model is not enough
- `NSFetchedResultsController` — driving a table/collection view from Core Data changes
- Faulting — objects are lazily loaded; accessing a fault outside its context's thread crashes

## Example

```swift
let backgroundContext = persistentContainer.newBackgroundContext()

backgroundContext.perform {
    let user = User(context: backgroundContext)
    user.name = "Trương"
    try? backgroundContext.save()
}
```

## Practice Questions

- Why must you never pass an `NSManagedObject` across threads directly?
- What happens if two contexts save conflicting changes to the same object?

## Senior Take

Most Core Data production bugs are threading bugs, not persistence bugs — an `NSManagedObject` fetched on a background context and touched on the main queue will crash intermittently under load, which makes it hard to catch in code review. Know the rule (one context per thread, pass `NSManagedObjectID` across contexts, not the object itself) and be able to explain why it exists.

## Exercise

Design a background import flow for a `Note` entity: parse 1,000 notes from JSON on a background context, save, then merge into the main context so a SwiftUI list updates. Write the merge policy you'd choose and explain what happens if the user edits a note in the UI while the background import is still running.
