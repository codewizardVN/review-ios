[English](./DesignPatterns.md) | [Tiếng Việt](./DesignPatterns.vi.md)

[← Architecture](./README.vi.md)

# Design Patterns

## Ý chính

MVC/MVVM/Clean Architecture mô tả cách một app hay feature được cấu trúc tổng thể. Bên dưới tầng đó, các design pattern kinh điển giải quyết những vấn đề nhỏ hơn, lặp lại bên trong các layer này — biết tên và trade-off của chúng quan trọng khi code review.

## Những điều cần nắm

- **Factory** — tập trung việc tạo object để nơi gọi không cần biết concrete type (ví dụ `ViewModelFactory` tạo ra view model với dependency đã được inject sẵn)
- **Repository** — trừu tượng hóa nguồn dữ liệu (network, cache, database) sau một protocol để phần còn lại của app không quan tâm dữ liệu đến từ đâu
- **Observer** — `NotificationCenter`, `Publisher` của Combine, và `@Published` đều là biến thể của pattern này; tách rời producer sự kiện khỏi consumer
- **Strategy** — hoán đổi một thuật toán/hành vi lúc runtime thông qua một protocol chung (ví dụ các strategy validation khác nhau theo từng loại field trong form)
- **Adapter** — bọc một API cũ hoặc bên thứ ba sau một interface mà app thực sự muốn dùng (thường gặp khi bridge một SDK Objective-C cũ sang interface async hiện đại)
- **Singleton** — thực sự hữu ích cho một số ít service mang tính toàn app thật sự (ví dụ logger), nhưng bị lạm dụng như một lối tắt thay cho dependency injection đúng cách — một dấu hiệu đỏ khi code review nếu áp dụng cho bất cứ thứ gì có state đáng kể hoặc cần fake trong test

## Ví dụ

```swift
protocol OrderRepository {
    func fetchOrders() async throws -> [Order]
}

final class RemoteOrderRepository: OrderRepository {
    private let client: APIClient
    init(client: APIClient) { self.client = client }

    func fetchOrders() async throws -> [Order] {
        try await client.get("/orders")
    }
}

final class InMemoryOrderRepository: OrderRepository {
    func fetchOrders() async throws -> [Order] { [] }
}
```

## Câu hỏi luyện tập

- Tại sao protocol `Repository` quan trọng cho testability hơn là cho chính implementation trong production?
- Khi nào Singleton là lựa chọn đúng, và khi nào nó là dấu hiệu dependency injection đã bị bỏ qua?

## Góc nhìn Senior

Gọi tên được pattern không phải là điểm mấu chốt — nhận ra khi nào một pattern đang bị áp dụng sai mới là điều quan trọng. Phát hiện phổ biến nhất khi code review ở tầm senior là "Singleton creep": các service giữ mutable state đáng kể bị expose thành `.shared`, khiến unit test gần như bất khả thi và che giấu coupling ngầm giữa các feature không liên quan. Một kỹ sư senior sẽ đẩy những trường hợp này về hướng dependency được inject qua constructor, kể cả khi phải gõ nhiều code hơn ban đầu.

## Bài tập

Refactor (trong comment/pseudocode) một singleton `NetworkManager.shared` xử lý auth token refresh, dựng request, và caching tất cả trong một class. Tách nó bằng Repository (truy cập dữ liệu theo từng resource), Strategy (retry policy có thể cắm theo từng loại endpoint), và constructor injection thay vì singleton dùng chung. Giải thích điều gì trở nên testable mà trước đó không thể.
