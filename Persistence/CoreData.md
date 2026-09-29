[English](./CoreData.md) | [Tiếng Việt](./CoreData.vi.md)

[← Persistence](./README.md)

# Core Data

## Key Idea

Core Data is an object graph and persistence framework, not just a database wrapper. `NSManagedObjectContext` tracks changes; `NSPersistentContainer` owns the stack and the underlying SQLite store.

## What To Review

- `NSManagedObjectContext` — main context (`viewContext`, bound to the main queue, used for UI) vs background context (private queue, used for writes/large imports); every access to a context and its objects must happen on that context's queue (for a background context, inside `perform`/`performAndWait`), never share a context across threads
- `NSPersistentContainer` / `NSPersistentCloudKitContainer` — stack setup, `newBackgroundContext()`
- Merge policies — decide who wins when two contexts change the same object: `NSMergeByPropertyObjectTrumpMergePolicy` (the saving context's in-memory values win) vs `NSMergeByPropertyStoreTrumpMergePolicy` (the values already in the store win); the default is `NSErrorMergePolicy`, meaning save throws on a conflict
- Lightweight vs manual migrations — lightweight migration infers the mapping for simple changes (adding an optional or defaulted attribute, a rename declared with a renaming identifier...); when data must be transformed (splitting/merging fields, changing types) you need a custom mapping model, or since iOS 17, staged migration (`NSStagedMigrationManager`)
- `NSFetchedResultsController` — driving a table/collection view from Core Data changes
- Faulting — objects come back as "faults" (empty shells) and their data is loaded only when you first read a property; if that read happens off the context's queue, it is a data race that can crash or return wrong data

## Example

```swift
import CoreData
import os

let logger = Logger(subsystem: "com.example.app", category: "CoreData")

let backgroundContext = persistentContainer.newBackgroundContext()
// Set the merge policy explicitly; the default is NSErrorMergePolicy (a conflict makes save throw)
backgroundContext.mergePolicy = NSMergePolicy.mergeByPropertyStoreTrump

backgroundContext.perform {
    let user = User(context: backgroundContext)
    user.name = "Trương"

    // Nothing changed, nothing to save (avoids needless I/O and notifications)
    guard backgroundContext.hasChanges else { return }
    do {
        try backgroundContext.save()
    } catch {
        // Do not use `try?`: the error (validation, merge conflict...) must be logged/surfaced,
        // then roll back so the context does not keep changes that could not be saved
        logger.error("Background save failed: \(error.localizedDescription)")
        backgroundContext.rollback()
    }
}
```

## Practice Questions

- Why must you never pass an `NSManagedObject` across threads directly?
- What happens if two contexts save conflicting changes to the same object?

## Senior Take

Most Core Data production bugs are threading bugs, not persistence bugs — an `NSManagedObject` fetched on a background context and touched on the main queue will crash intermittently under load, which makes it hard to catch in code review. Know the rule (one context per thread, pass `NSManagedObjectID` across contexts, not the object itself) and be able to explain why it exists.

## Practice Question Answers

### Why must you never pass an `NSManagedObject` across threads directly?

Because an `NSManagedObject` belongs to exactly one `NSManagedObjectContext`, and that context may only be used on its own queue; touching the object from another queue is a data race that can crash or return wrong data.

How it works: a managed object does not hold its data independently. Many objects are faults — when you read `note.title`, the object calls back into its context to fetch data from the row cache or the store. The context is not thread-safe, so reading from another thread means two threads operating on the context's internal state at once. The bug does not happen every time, only when both sides collide at the wrong moment, which is why it tends to surface under load in production.

The correct approach is to pass the `NSManagedObjectID` — which is safe to share across threads — and re-fetch the object in the destination context:

```swift
let id = note.objectID
try await viewContext.perform {
    let noteOnMain = try viewContext.existingObject(with: id) as? Note
    // use noteOnMain on viewContext's queue
}
```

Note: a newly inserted object has a temporary ID until you save or call `obtainPermanentIDs(for:)`. While debugging, enable the launch argument `-com.apple.CoreData.ConcurrencyDebug 1` so Core Data crashes right at the wrong-queue access instead of randomly later. In Swift 6, `NSManagedObject` is not `Sendable`, so the compiler also flags passing it across an isolation boundary.

Trade-off: if you only need to display data, mapping the object into a value struct (a snapshot) is also safe, at the cost of losing automatic updates from the context.

### What happens if two contexts save conflicting changes to the same object?

It depends on the merge policy of the context that saves second: with the default policy (`NSErrorMergePolicy`), that save fails with a merge conflict error; with the other policies, Core Data resolves it property by property.

How it works: each context keeps a snapshot of the object from when it fetched it. On save, Core Data compares that snapshot with the current value in the store (optimistic locking). If another context has changed the store in the meantime, that is a conflict:
- `NSErrorMergePolicy` (default): `save()` throws an error with code `NSManagedObjectMergeError` — if the code uses `try? save()`, the error is swallowed and the data is silently not saved; that is why the example in this file catches the error with `do/catch`.
- `NSMergeByPropertyObjectTrumpMergePolicy`: the in-memory values of the saving context win, but only for properties it changed; other properties take the store's values.
- `NSMergeByPropertyStoreTrumpMergePolicy`: the store's values win for conflicting properties.
- `NSOverwriteMergePolicy`: the whole object is overwritten with the in-memory version.

For the `Note` exercise: if the background import uses StoreTrump and `viewContext` uses ObjectTrump, the user's edits in the UI win no matter who saves first, and the import does not overwrite fields the user just edited. Do not forget `viewContext.automaticallyMergesChangesFromParent = true` so the UI receives changes from background saves.

Trade-off: no policy is "right" in every case; choose based on which source is more trustworthy for each kind of data. When you need more complex logic (version-based merging), you can subclass `NSMergePolicy`.

## Interview Traps

### Does the default merge policy resolve conflicts automatically?

**Common wrong answer:** "Yes, Core Data merges automatically and the last save wins."

**Better answer:** The default is `NSErrorMergePolicy`, which resolves nothing: `save()` throws a merge conflict error. If the code uses `try? context.save()`, the changes are lost without anyone noticing. Set `mergePolicy` explicitly on both `viewContext` and background contexts, and log save errors instead of swallowing them.

### After running an `NSBatchInsertRequest`, does the SwiftUI list update automatically?

**Common wrong answer:** "Yes, because `automaticallyMergesChangesFromParent` is enabled."

**Better answer:** Batch insert/update/delete writes directly to the SQLite store and bypasses the context, so there is no save notification to merge, and merge policies do not apply either. Ask the request to return object IDs (`resultType = .objectIDs`) and call `NSManagedObjectContext.mergeChanges(fromRemoteContextSave:into:)`, or enable persistent history tracking and process the history. In return, batching is much faster and uses far less memory than creating 1,000 objects in a context.

### "One context per thread" — so it is enough to use a background context on one fixed thread?

**Common wrong answer:** "Right, I create a dedicated background thread and use the context there."

**Better answer:** For a `privateQueueConcurrencyType` context (such as one from `newBackgroundContext()`), the real rule is "only touch the context inside `perform`/`performAndWait`", because the context owns its queue and the executing thread may differ between calls. Calling it directly outside `perform`, even from a "fixed" thread, is still wrong. `viewContext` is the exception: it is bound to the main queue, so using it directly on the main thread (or in `@MainActor` code) is valid.

## Exercise

Design a background import flow for a `Note` entity: parse 1,000 notes from JSON on a background context, save, then merge into the main context so a SwiftUI list updates. Write the merge policy you'd choose and explain what happens if the user edits a note in the UI while the background import is still running.
