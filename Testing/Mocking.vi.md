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

## Câu hỏi luyện tập

- Mock khác stub ở điểm nào?
- Bạn nên dùng mocking framework hay tự viết fake thủ công?

## Góc nhìn senior

Fake viết tay thường rõ ràng và an toàn hơn mock được sinh tự động. Mocking framework có thể che khuất điều thực sự đang được kiểm tra. Chỉ dùng framework khi fake sẽ quá phức tạp để viết thủ công.

## Đáp án câu hỏi luyện tập

### Mock khác stub ở điểm nào?

Stub chỉ *cung cấp dữ liệu* cho code đang test, còn mock *kiểm tra tương tác*: nó xác minh rằng code đã gọi đúng method, đúng số lần, với đúng tham số.

Hiểu theo hướng của dữ liệu:

- **Stub** lo đầu vào gián tiếp. Ví dụ `stubbedItems` trong `FakeFeedRepository` quyết định `fetchFeed()` trả về gì. Test sau đó assert trên *output* của SUT, như `sut.items.count == 1`. Stub không bao giờ làm test fail.
- **Mock** lo đầu ra gián tiếp, tức những thứ SUT "gửi đi" mà không trả về: gửi analytics, ghi log, gọi API xoá. Assertion nằm trên chính test double, ví dụ "`trackPurchase` được gọi đúng một lần".

Trong Swift, ranh giới hay bị trộn: `FakeFeedRepository` vừa là stub (qua `stubbedItems`) vừa là spy (qua `fetchCallCount` ghi lại lời gọi để assert sau). Điều quan trọng là biết test đang kiểm tra *state* hay *interaction*.

Khi nào không nên dùng mock: khi có thể kiểm tra kết quả qua state. Verify tương tác quá chi tiết (thứ tự gọi, tham số phụ) làm test gắn chặt vào implementation, refactor một chút là vỡ dù hành vi vẫn đúng. Chỉ verify interaction khi chính lời gọi đó là hành vi cần đảm bảo, như gửi event thanh toán hoặc không gọi API hai lần.

### Bạn nên dùng mocking framework hay tự viết fake thủ công?

Mặc định nên tự viết fake thủ công dựa trên protocol; chỉ dùng framework hoặc code generation khi số lượng protocol lớn đến mức viết tay trở thành gánh nặng.

Lý do fake viết tay phù hợp với Swift:

- Swift không có runtime mocking như Mockito bên Java: struct, `final class` và method không `dynamic` được dispatch tĩnh hoặc qua vtable cố định lúc compile, Swift thuần không cho thay implementation của method lúc runtime (không có swizzling), còn `Mirror` chỉ đọc được giá trị chứ không sửa được hành vi. Các công cụ Swift (Mockolo, Sourcery, Cuckoo, hoặc macro như Spyable) đều *sinh code* lúc build, nên vẫn phải có protocol.
- Fake viết tay dễ đọc: người review thấy ngay `fetchFeed()` trả về gì mà không phải học DSL của framework.
- Fake dùng lại được giữa nhiều test và có thể có hành vi thật, ví dụ in-memory repository lưu và đọc dữ liệu.
- Compiler kiểm tra đầy đủ; đổi protocol là fake báo lỗi ngay.

Khi framework đáng dùng: codebase có hàng trăm protocol với nhiều method, fake chủ yếu là boilerplate đếm lời gọi. Code generation tiết kiệm thời gian, đổi lại thêm bước build, thêm dependency, và test thường verify interaction nhiều hơn mức cần thiết. Senior nên chọn theo quy mô và ghi rõ quy ước cho team.

## Bẫy phỏng vấn

### "`FakeFeedRepository` trong ví dụ là fake, đúng không?"

**Dễ trả lời sai:** Đúng, vì tên của nó có chữ "Fake" và nó implement protocol.

**Nên trả lời:** Tên gọi không quyết định loại test double. Theo định nghĩa chặt, class này là stub (trả về `stubbedItems` cố định) kết hợp spy (đếm `fetchCallCount`), chứ không phải fake, vì nó không có hành vi thật. Một fake đúng nghĩa sẽ có logic hoạt động, ví dụ lưu item vào dictionary khi `save()` và trả lại khi `fetch()`. Trong thực tế nhiều team gọi chung là "fake", nhưng khi phỏng vấn nên phân biệt được để cho thấy bạn hiểu test đang kiểm tra state hay interaction.

### "Có thể mock `URLSession` hay một `final class` bất kỳ bằng framework như Mockito không?"

**Dễ trả lời sai:** Được, chỉ cần một thư viện mocking là có thể thay method của bất kỳ class nào lúc runtime.

**Nên trả lời:** Với Swift thuần thì không. Lời gọi tới `final class` và struct được dispatch tĩnh; method của class không `final` đi qua vtable, nhưng vtable được cố định lúc compile nên chỉ có thể thay hành vi bằng cách tự viết subclass override, chứ không có cách chèn mock lúc runtime như Mockito. OCMock dựa vào Objective-C runtime nên chỉ hoạt động với class Objective-C/`NSObject` và method được gọi qua message dispatch (`@objc dynamic`), không phải giải pháp chung cho code Swift. (`URLSession` là class Objective-C không `final`, nhưng subclass nó để mock là cách Apple không khuyến khích, và `URLSession.init()` đã deprecated từ iOS 13.) Cách đúng là đặt protocol ở ranh giới (ví dụ `FeedRepository`) và thay implementation; với `URLSession` cụ thể thì có thể dùng `URLProtocol` tuỳ biến trong `URLSessionConfiguration.protocolClasses` để chặn request mà không cần mock class.

### "Swift 6 báo lỗi khi `FakeFeedRepository` conform protocol yêu cầu `Sendable`. Thêm `@unchecked Sendable` là xong?"

**Dễ trả lời sai:** Đúng, đây chỉ là code test nên tắt kiểm tra là được.

**Nên trả lời:** `@unchecked Sendable` chỉ tắt cảnh báo, không làm class an toàn; nếu test (nhất là Swift Testing chạy song song) gọi fake từ nhiều thread thì `fetchCallCount += 1` là data race thật và gây kết quả sai ngẫu nhiên. Cách an toàn hơn là bảo vệ state bằng `Mutex` từ module Synchronization (cần iOS 18+ / macOS 15+ và toolchain Swift 6): lưu nó trong `let` của một `final class` thì class có thể conform `Sendable` thật sự mà không cần `@unchecked`. Nếu phải hỗ trợ iOS cũ hơn thì dùng `OSAllocatedUnfairLock` (iOS 16+) hoặc `NSLock` (với `NSLock` vẫn phải dùng `@unchecked Sendable`, nhưng lúc này bạn thật sự đã bảo vệ state). Một lựa chọn khác là biến fake thành `actor` khi method của protocol đã là `async`. Nếu SUT luôn chạy trên main actor thì cũng có thể đánh dấu fake `@MainActor`.

## Bài tập

Tạo `FakeAnalyticsService` ghi lại tên mỗi event được truyền vào. Inject nó vào `CheckoutViewModel` và assert rằng `trackPurchase()` được gọi đúng một lần sau khi đặt hàng thành công. Sau đó giải thích: đây là mock, stub, hay spy?
