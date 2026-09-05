[English](./StructuredConcurrency.md) | [Tiếng Việt](./StructuredConcurrency.vi.md)

[← Concurrency](./README.vi.md)

# Structured Concurrency

## Ý chính

Structured concurrency gắn lifetime của child task vào parent scope. Khi parent scope kết thúc — dù bình thường hay do cancellation — child task được tự động cancel.

## Nội dung ôn tập

- `async let` — bắt đầu công việc đồng thời và await sau
- `withTaskGroup` / `withThrowingTaskGroup` — dynamic fan-out
- Task hierarchy — parent tự động cancel child
- Task priority propagation

## Ví dụ

```swift
func loadDashboard() async throws -> Dashboard {
    async let user = fetchUser()
    async let feed = fetchFeed()
    return try await Dashboard(user: user, feed: feed)
}
```

```swift
func fetchAll(ids: [String]) async throws -> [Item] {
    try await withThrowingTaskGroup(of: Item.self) { group in
        for id in ids {
            group.addTask { try await fetchItem(id: id) }
        }
        return try await group.reduce(into: []) { $0.append($1) }
    }
}
```

## Câu hỏi luyện tập

- Khi nào async let rõ ràng hơn cho một function loadProfile() fetch đồng thời user, posts và followers, và khi nào withThrowingTaskGroup trở nên cần thiết thay thế?

## Góc nhìn Senior

Structured concurrency không chỉ là tiện ích cú pháp. Nó cung cấp mô hình ownership rõ ràng: task được giới hạn scope, leak khó xảy ra hơn, và cancellation tự động lan truyền. Ưu tiên dùng structured concurrency thay vì `Task { }` không có cấu trúc khi lifetime được giới hạn.

## Bài tập

Viết function `loadProfile() async throws -> Profile` fetch `user`, `posts`, và `followers` đồng thời dùng `async let`. Sau đó viết lại function tương tự dùng `withThrowingTaskGroup` để tập hợp requests có thể được điều khiển bởi dynamic array. Viết comment so sánh hai cách: khi nào `async let` rõ ràng hơn, khi nào `TaskGroup` trở nên cần thiết?
