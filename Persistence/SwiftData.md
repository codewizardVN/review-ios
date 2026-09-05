[English](./SwiftData.md) | [Tiếng Việt](./SwiftData.vi.md)

[← Persistence](./README.md)

# SwiftData

## Key Idea

SwiftData is Apple's Swift-native persistence framework built on top of Core Data's storage engine, using macros (`@Model`) instead of the `.xcdatamodeld` editor.

## What To Review

- `@Model` — turns a plain Swift class into a persisted entity, macro-generated storage
- `ModelContainer` / `ModelContext` — analogous to `NSPersistentContainer` / `NSManagedObjectContext`
- `@Query` — declarative fetch inside SwiftUI views, auto-updates on change
- Migration — `SchemaMigrationPlan` for versioned schema changes
- Relationship to Core Data — same underlying store; SwiftData is the API layer, not a replacement engine

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

## Exercise

Sketch (in comments) a decision matrix comparing Core Data vs SwiftData for: a brand-new SwiftUI-only app, and an existing UIKit + Core Data app with 3 years of user data and CloudKit sync. State which you'd pick for each and why, including one concrete migration risk for the second case.
