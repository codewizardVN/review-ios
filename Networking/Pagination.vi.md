[English](./Pagination.md) | [Tiếng Việt](./Pagination.vi.md)

[← Data và Networking](./README.vi.md)

# Pagination

## Ý chính

Pagination là bài toán tải thêm dữ liệu theo cách ổn định, không tạo request trùng, không vỡ thứ tự dữ liệu, và không làm loading state rối rắm.

## Cần ôn

- Pagination kiểu offset vs cursor
- Ai sở hữu paging state
- Cách tránh duplicate load khi scroll nhanh
- Cách merge các page mà vẫn giữ identity

## Ví dụ

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

## Câu hỏi thực hành

- Paging state nên nằm ở ViewModel hay service?
- Làm sao tránh load page 3 hai lần?

## Góc nhìn senior

Paging state thường nên nằm gần feature flow, không nên chôn quá sâu trong một generic network client. Điều quan trọng là ownership rõ ràng cho `isLoading`, `nextCursor`, và cách merge dữ liệu.

## Bài tập

Mô hình hóa một infinite feed dùng cursor pagination. Mô tả các state: success, empty, loading-more, error. Sau đó giải thích cách bạn ngăn duplicate request khi user chạm đáy danh sách nhiều lần.
