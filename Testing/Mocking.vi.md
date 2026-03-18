[English](./Mocking.md) | [Tiếng Việt](./Mocking.vi.md)

[← Testing](./README.vi.md)

# Mocking và Test Doubles

## Các loại Test Double

| Loại | Mô tả |
| --- | --- |
| **Stub** | Trả về giá trị cố định; không kiểm tra lời gọi |
| **Mock** | Xác minh rằng các lời gọi cụ thể đã được thực hiện |
| **Fake** | Triển khai nhẹ có hoạt động thật (ví dụ: in-memory repository) |
| **Spy** | Ghi lại các lời gọi để assert sau |

## Cách tiếp cận ưu tiên trong Swift

Dùng protocol-based fakes. Định nghĩa protocol, triển khai phiên bản thật trong production, và triển khai phiên bản `Fake` trong tests.

```swift
protocol FeedRepository {
    func fetchFeed() async throws -> [FeedItem]
}

// Test fake
final class FakeFeedRepository: FeedRepository {
    var stubbedItems: [FeedItem] = []
    var fetchCallCount = 0

    func fetchFeed() async throws -> [FeedItem] {
        fetchCallCount += 1
        return stubbedItems
    }
}
```

## Câu hỏi thực hành

- Mock khác stub như thế nào?
- Nên dùng mocking framework hay viết fake thủ công?

## Góc nhìn senior

Fake viết tay thường rõ ràng và an toàn hơn mock được sinh tự động. Mocking framework có thể che khuất điều thực sự đang được kiểm tra. Chỉ dùng framework khi fake sẽ quá phức tạp để viết thủ công.

## Bài tập

Tạo `FakeAnalyticsService` ghi lại tên mỗi event được truyền vào. Inject nó vào `CheckoutViewModel` và assert rằng `trackPurchase()` được gọi đúng một lần sau khi đặt hàng thành công. Sau đó giải thích: đây là mock, stub, hay spy?
