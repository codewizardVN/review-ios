[English](./Pagination.md) | [Tiếng Việt](./Pagination.vi.md)

[← Data and Networking](./README.md)

# Pagination

## Key Idea

Pagination is about loading additional data predictably without duplicate requests, broken ordering, or poor loading states.

## What To Review

- Offset-based vs cursor-based pagination
- Who owns paging state
- Preventing duplicate loads when scrolling fast
- Merging pages while preserving identity

## Example

```swift
struct FeedPage {
    let items: [FeedItem]
    let nextCursor: String?
}

protocol FeedRepository: Sendable {
    // repository.fetchFeed(cursor:) is stateless: it remembers no cursor between calls
    func fetchFeed(cursor: String?) async throws -> FeedPage
}

// @MainActor: every call runs on the main actor, so the "check isLoading, then set it to true"
// step runs in one go before the first `await` (see the answers below)
@MainActor
final class FeedPager {
    private let repository: any FeedRepository
    private(set) var nextCursor: String?
    private(set) var isLoading = false
    // nextCursor == nil after the last page: without this flag the next call would reload page 1
    private(set) var hasMore = true

    init(repository: any FeedRepository) {
        self.repository = repository
    }

    func loadNextPage() async throws -> FeedPage? {
        guard !isLoading, hasMore else { return nil }  // skip if already loading or no more pages
        isLoading = true
        defer { isLoading = false }

        let page = try await repository.fetchFeed(cursor: nextCursor)
        nextCursor = page.nextCursor
        hasMore = page.nextCursor != nil
        return page
    }
}
```

## Practice Questions

- Should pagination state live in the ViewModel or service?
- How do you avoid loading page 3 twice?

## Senior Take

Paging state often belongs close to the feature flow, not deep inside a generic network client. The important part is explicit ownership of `isLoading`, `nextCursor`, and merge behavior.

## Practice Question Answers

### Should pagination state live in the ViewModel or service?

Paging state should live close to the feature — in the ViewModel or a dedicated object like `FeedPager` that the ViewModel owns — while the service (network client) should stay stateless.

The reason is that paging state belongs to one specific viewing session: this list, with this filter, starting when the user opened the screen. `nextCursor`, `isLoading`, the merged item list and the reset on pull-to-refresh all share the screen's lifecycle. If you put them in a shared service (often a singleton), two screens using the feed with different filters overwrite each other's cursor, and stale state is still there when the user comes back.

A common split:
- **Service/repository**: `fetchFeed(cursor: String?) async throws -> FeedPage` — remembers nothing between calls.
- **Pager**: holds `nextCursor` and `isLoading`, prevents duplicate requests, merges and dedupes items by `id`.
- **ViewModel**: turns pager state into UI state (`loading`, `loaded`, `empty`, `loadingMore`, `error`).

Separating `FeedPager` from the ViewModel lets you test paging logic without UI and reuse it across several feed screens.

Trade-off: for a simple screen, keeping state directly in the ViewModel is enough; an extra pager is only worth it once merge/dedupe logic gets complicated. If the feed needs long-lived caching or offline support, the items themselves should live in the repository/database, but the cursor of the current session still belongs to the feature.

### How do you avoid loading page 3 twice?

Block it at several layers: do not send a second request while one for the same page is in flight, discard results that have become stale, and dedupe items on merge in case something still slips through.

The first layer is the `isLoading` guard in `FeedPager`, but it is only correct when every call runs on the same executor. Mark the pager (or ViewModel) `@MainActor` so the "check, then mark as loading" step runs in one go before the first `await`; without isolation, two calls from two threads can both pass the guard.

The second layer avoids stale results: on pull-to-refresh, cancel the in-flight load-more `Task` or bump a `generation` counter, and discard a response whose generation has changed.

The third layer is merging by identity: when appending, skip items whose `id` already exists (use a `Set` of ids). This also handles a backend that returns the same item on two pages.

```swift
@MainActor
final class FeedPager {
    private var loadTask: Task<Void, Never>?

    func loadNextPageIfNeeded() {
        guard loadTask == nil else { return }  // a request is already in flight
        loadTask = Task {
            defer { loadTask = nil }
            // fetch with nextCursor, merge, dedupe by id
        }
    }
}
```

Trade-off: debouncing the scroll trigger also reduces requests, but it does not replace the guard — debouncing only thins requests out, it does not guarantee each page is requested once.

## Interview Traps

### "Using an actor for the pager eliminates race conditions" — true?

**Common wrong answer:** "Yes, an actor serializes all access, so duplicate loads are impossible."

**Better answer:** An actor prevents data races, but not logic races, because actors are reentrant: at every `await`, the actor may process another call. If you `guard !isLoading` and then `await` something before setting `isLoading = true`, a second call still gets past the guard. You must check and mark state before the first `await`, and re-check state after the `await` returns (for example, whether the cursor still matches).

### What is wrong with offset pagination (`?page=3&limit=20`) for a feed?

**Common wrong answer:** "Nothing, offsets are simple and even let you jump straight to any page."

**Better answer:** When new items are inserted at the top of the feed while the user is scrolling, every offset shifts: page 3 contains a few items from page 2 again (duplicates) or skips items. A cursor (usually the id or timestamp of the last item) is tied to a real position in the data, so it is more stable, and the database query is faster than an `OFFSET` over thousands of rows. Offsets still fit data that rarely changes and needs page jumping, such as numbered search result pages.

### What happens if the user pulls to refresh while a load-more is in flight?

**Common wrong answer:** "Nothing, the `isLoading` guard handles it."

**Better answer:** If refresh resets the list and the cursor, the old load-more response arrives later and gets appended to the new list — mixed-up data and a wrong cursor. Cancel the load-more `Task` on refresh, or tag each request with a generation/token and discard results that do not match. Also, in SwiftUI the last row's `.onAppear` can fire several times as layout changes, so the load-more trigger must be idempotent.

## Exercise

Model an infinite feed with cursor pagination. Describe the success, empty, loading-more, and error states. Then explain how you would prevent duplicate requests when the user reaches the bottom repeatedly.
