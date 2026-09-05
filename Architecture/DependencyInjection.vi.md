[English](./DependencyInjection.md) | [Tiếng Việt](./DependencyInjection.vi.md)

[← Architecture](./README.vi.md)

# Dependency Injection

## Ý chính

Truyền dependency từ bên ngoài vào thay vì tạo bên trong. Điều này giúp component dễ test, dễ thay thế và rõ ràng về những gì nó cần.

## Các hướng tiếp cận

### 1. Constructor injection (ưu tiên)

```swift
final class FeedViewModel {
    private let repository: FeedRepository

    init(repository: FeedRepository) {
        self.repository = repository
    }
}
```

### 2. Property injection

```swift
final class FeedViewModel {
    var repository: FeedRepository = RemoteFeedRepository()
}
```

### 3. Environment / Service Locator

Hữu ích trong SwiftUI qua `.environment()` hoặc shared container, nhưng ẩn dependency và làm luồng khó trace hơn.

## Tại sao quan trọng

- Swap real implementation bằng fake trong test
- Dependency tường minh tự document
- Không có hidden global state

## Câu hỏi thực hành

- DI giúp testing như thế nào?
- Tiêu chí nào để quyết định giữa DI container và manual injection?

## Câu hỏi luyện tập

- Dependency injection giúp ích cho việc testing như thế nào?
- Bạn dùng tiêu chí gì để quyết định giữa DI container và inject thủ công?

## Góc nhìn Senior

Manual DI thường đủ cho hầu hết app. Dùng DI container (như Needle hoặc Swinject) chỉ khi dependency graph lớn và phức tạp. Container thêm độ phức tạp và learning curve riêng.

## Bài tập

Lấy `CheckoutViewModel` gọi `PaymentService()` và `AnalyticsService.shared` bên trong. Refactor: (1) tạo `PaymentServiceProtocol` và `AnalyticsProtocol`, (2) chuyển sang constructor injection. Viết hai test: một xác nhận analytics track `"purchase_complete"` khi payment thành công, một xác nhận nó KHÔNG track khi thất bại. Giải thích tại sao constructor injection được ưu tiên hơn property injection cho required dependency.
