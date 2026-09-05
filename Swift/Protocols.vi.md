[English](./Protocols.md) | [Tiếng Việt](./Protocols.vi.md)

[← Swift Core](./README.vi.md)

# Protocol-Oriented Programming

## Ý chính

Protocol giúp định nghĩa các behavior contract và giảm thiểu sự phụ thuộc. Chúng đặc biệt hữu ích cho testability, composability, và API boundaries.

## Ví dụ

```swift
protocol UserRepository {
    func fetchUser(id: String) async throws -> User
}
```

## Cách trả lời cấp Senior

- Protocol hữu ích tại các ranh giới (boundaries)
- Quá nhiều protocol có thể làm codebase trở nên phức tạp không cần thiết
- Protocol nên tồn tại khi có nhu cầu substitution hoặc abstraction thực sự

## Câu hỏi luyện tập

- Tại sao việc inject protocol AnalyticsService (với FirebaseAnalytics và NoOpAnalytics) vào initializer của CheckoutViewModel lại giúp ViewModel có thể test được?

## Bài tập

Định nghĩa một protocol `AnalyticsService` với một method duy nhất `track(event: String)`. Viết hai conforming type: `FirebaseAnalytics` (chỉ in "Firebase: \(event)") và `NoOpAnalytics` (không làm gì). Inject `AnalyticsService` vào `CheckoutViewModel` thông qua initializer của nó. Viết một unit test sử dụng `NoOpAnalytics`. Giải thích tại sao protocol boundary giúp ViewModel có thể test được.
