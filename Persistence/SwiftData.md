[English](./SwiftData.md) | [Tiếng Việt](./SwiftData.vi.md)

[← Persistence](./README.md)

# SwiftData

## Key Idea

SwiftData is Apple's Swift-native persistence framework built on top of Core Data's storage engine, using macros (`@Model`) instead of the `.xcdatamodeld` editor.

## What To Review

- `@Model` — a macro that turns a plain Swift class into a persisted entity: it generates storage code for each stored property and makes the class conform to `PersistentModel` and `Observable`, so SwiftUI updates when a property changes
- `ModelContainer` / `ModelContext` — analogous to `NSPersistentContainer` / `NSManagedObjectContext`
- `@Query` — declarative fetch inside SwiftUI views, auto-updates on change
- Migration — `SchemaMigrationPlan` for versioned schema changes
- Relationship to Core Data — SwiftData's default store is Core Data's SQLite store; SwiftData is a new API layer on top, not a replacement engine (since iOS 18 you can write a custom data store via the `DataStore` protocol, but that is rarely needed)

## Example

```swift
@Model
final class Note {
    var title: String
    var body: String
    var createdAt: Date

    init(title: String, body: String, createdAt: Date = .now) {
        self.title = title
        self.body = body
        self.createdAt = createdAt
    }
}

struct NoteListView: View {
    @Query(sort: \Note.createdAt, order: .reverse) private var notes: [Note]
    @Environment(\.modelContext) private var context

    var body: some View {
        List(notes) { Text($0.title) }
    }
}
```

## Practice Questions

- What are the trade-offs of adopting SwiftData in an app that already has years of Core Data data?
- Why does `@Query` reduce the need for `NSFetchedResultsController`-style boilerplate?

## Senior Take

SwiftData is attractive for greenfield SwiftUI apps, but for an existing production app with a mature Core Data model, migration cost and edge-case gaps (complex fetch requests, some CloudKit sync scenarios) often outweigh the ergonomics gain. A senior call here is not "which is newer" but "what does the migration actually cost against the current schema and sync setup."

## Practice Question Answers

### What are the trade-offs of adopting SwiftData in an app that already has years of Core Data data?

The benefit is a leaner Swift-native API with good SwiftUI integration; the cost is risk to real user data, an iOS 17+ requirement and some feature gaps compared with Core Data.

Points to weigh:
- **Reusing the old store is not automatic.** SwiftData can open the Core Data SQLite file itself, but `@Model` must match the entity, attribute and relationship names; different names need `@Attribute(originalName:)`, and the store URL must point at the old file. One mistake means lost data or a store that will not open.
- **Coexistence**: you can run Core Data and SwiftData side by side on the same store during a transition, but you must keep the two model definitions in sync and enable persistent history tracking.
- **Deployment target**: SwiftData needs iOS 17, and many important improvements (`#Unique`, `#Index`, custom data stores, many bug fixes) arrived only in iOS 18, so an app still supporting iOS 16 cannot use it yet.
- **Feature gaps**: no full equivalent of `NSFetchedResultsController` with sections, `#Predicate` is more limited than `NSPredicate`, no batch insert/update, less control over faulting and prefetching.
- **CloudKit**: SwiftData's automatic sync only supports the private database; as of iOS 26 it does not support sharing (`CKShare`) or the public database the way `NSPersistentCloudKitContainer` does.

Practical trade-off: for a stable app, it is usually better to keep Core Data, or use SwiftData only for new features with a separate store, and reassess once old iOS versions are dropped. Migrate everything only when the benefit is clear and you have tested on a copy of real user data.

### Why does `@Query` reduce the need for `NSFetchedResultsController`-style boilerplate?

Because `@Query` wraps the whole "fetch, observe changes, and tell the UI to re-render" job in a property wrapper, so the view just declares the data it needs instead of managing a controller and a delegate.

With `NSFetchedResultsController` in UIKit, you must create an `NSFetchRequest` with sort descriptors, initialize the controller with a context, call `performFetch()`, implement the delegate (`controllerDidChangeContent` or `didChangeContentWith` a snapshot), and apply the snapshot to a diffable data source. `@Query` does all of that implicitly: it takes `modelContext` from the environment, runs the fetch with the sort/filter you declared, observes changes in the context, and when the data changes SwiftUI re-renders `body`. In `NoteListView`, the single line `@Query(sort: \Note.createdAt, order: .reverse)` replaces dozens of lines of setup.

Limits to know:
- `@Query` only works inside a SwiftUI `View`; a ViewModel or service must use a `FetchDescriptor` with `modelContext.fetch`, which does not observe changes on its own.
- For dynamic filtering (a search field), you rebuild the query in the view's `init` with `Query(filter:sort:)` from the passed-in parameters.
- There are no built-in sections like FRC; you group items yourself.
- The fetch runs on the main context, so for large data sets set a `fetchLimit` via a `FetchDescriptor`.

Trade-off: the convenience comes from tying the query tightly to the view, so query logic is hard to test in isolation and hard to reuse outside SwiftUI.

## Interview Traps

### Can you pass an `@Model` object to a background task for processing?

**Common wrong answer:** "Yes, `@Model` is just a normal Swift class, so pass it like any object."

**Better answer:** A model object is bound to the `ModelContext` that fetched it and is not `Sendable`, just like `NSManagedObject`; Swift 6 reports an error when you send it across an actor boundary. Pass its `persistentModelID` (a `PersistentIdentifier`, which is `Sendable`), then inside an actor marked `@ModelActor` (which has its own context) re-fetch the object, for example with `self[id, as: Note.self]` or `modelContext.model(for:)` (which returns `any PersistentModel` and needs a cast).

### If you rename a property in an `@Model` (say `body` to `content`), does lightweight migration handle it?

**Common wrong answer:** "Yes, SwiftData detects it and migrates."

**Better answer:** SwiftData cannot guess a rename: it treats it as deleting the `body` attribute and adding a new `content` attribute, so the old data is lost. Declare `@Attribute(originalName: "body") var content: String` so lightweight migration maps it correctly. For more complex changes (splitting a field, changing a type), you need a `VersionedSchema` and `MigrationStage.custom` in a `SchemaMigrationPlan`.

### Is enabling CloudKit sync for an existing model just a matter of adding `cloudKitDatabase` to the `ModelConfiguration`?

**Common wrong answer:** "Yes, enable the capability and configure the container, done."

**Better answer:** CloudKit places constraints on the schema: no unique constraints (`@Attribute(.unique)`, `#Unique`), every relationship must be optional, and every property must be optional or have a default value. A model that breaks these rules makes the container fail to load once sync is enabled. Also, the production CloudKit schema is additive only — you cannot delete or change fields — so design carefully before deploying the schema.

## Exercise

Sketch (in comments) a decision matrix comparing Core Data vs SwiftData for: a brand-new SwiftUI-only app, and an existing UIKit + Core Data app with 3 years of user data and CloudKit sync. State which you'd pick for each and why, including one concrete migration risk for the second case.
