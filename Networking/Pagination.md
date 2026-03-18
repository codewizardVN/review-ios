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

final class FeedPager {
    private(set) var nextCursor: String?
    private(set) var isLoading = false

    func loadNextPage() async throws -> FeedPage? {
        guard !isLoading else { return nil }
        isLoading = true
        defer { isLoading = false }

        let page = try await repository.fetchFeed(cursor: nextCursor)
        nextCursor = page.nextCursor
        return page
    }
}
```

## Practice Questions

- Should pagination state live in the ViewModel or service?
- How do you avoid loading page 3 twice?

## Senior Take

Paging state often belongs close to the feature flow, not deep inside a generic network client. The important part is explicit ownership of `isLoading`, `nextCursor`, and merge behavior.

## Exercise

Model an infinite feed with cursor pagination. Describe the success, empty, loading-more, and error states. Then explain how you would prevent duplicate requests when the user reaches the bottom repeatedly.
