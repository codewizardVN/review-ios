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

## Đáp án câu hỏi luyện tập

### Tại sao protocol `Repository` quan trọng cho testability hơn là cho chính implementation trong production?

Vì trong production gần như lúc nào cũng chỉ có một implementation là `RemoteOrderRepository`; giá trị hằng ngày của protocol nằm ở chỗ nó tạo ra một "đường nối" để test và preview thay bằng `InMemoryOrderRepository`.

Cơ chế: ViewModel hay use case phụ thuộc vào `OrderRepository` chứ không phụ thuộc concrete type. Composition root quyết định lắp bản nào. Trong test, bạn lắp bản in-memory trả sẵn danh sách order hoặc ném lỗi, nên kiểm tra được logic hiển thị, trạng thái rỗng, trạng thái lỗi mà không cần mạng. SwiftUI preview cũng dùng lại chính bản fake này.

Lý do hay được nêu là "sau này đổi từ REST sang GraphQL hay thêm cache chỉ cần viết implementation mới". Điều đó có thật nhưng hiếm, và khi xảy ra thì shape của protocol thường cũng phải đổi theo: phân trang, cache, offline khiến abstraction bị rò. Vì vậy hãy thành thật: protocol được biện minh chủ yếu bởi test và preview.

Trade-off và cách làm đúng:

- Thiết kế protocol theo nhu cầu của consumer (`fetchOrders()`), đừng copy nguyên danh sách endpoint.
- Nếu một chỗ không cần thay thế trong test, như hàm map thuần, thì không cần protocol.
- Một đường nối nhẹ hơn cũng được: inject closure `fetchOrders: () async throws -> [Order]` hoặc một struct chứa các closure.

### Khi nào Singleton là lựa chọn đúng, và khi nào nó là dấu hiệu dependency injection đã bị bỏ qua?

Singleton đúng khi bản chất chỉ có một instance và state của nó không ảnh hưởng tới kết quả test; nó là dấu hiệu DI bị bỏ qua khi `.shared` giữ mutable state quan trọng và được gọi sâu bên trong các class.

Trường hợp hợp lý: logger (ví dụ bọc `os.Logger`), các object hệ thống như `FileManager.default`, `NotificationCenter.default`, `UIApplication.shared`. Chúng gần như không có state nghiệp vụ, và test không cần kiểm tra chúng.

Dấu hiệu có vấn đề:

- `.shared` giữ session, giỏ hàng, token, cache.
- Test phải "reset" singleton giữa các case, hoặc kết quả test phụ thuộc thứ tự chạy.
- Nhìn `init` của một class không biết nó thật sự dùng những gì.

Cần phân biệt hai thứ: "chỉ có một instance" là chuyện vòng đời, còn "truy cập qua global" là chuyện coupling. Bạn có thể giữ một instance duy nhất nhưng vẫn inject nó: tạo một lần ở composition root rồi truyền qua `init`, hoặc dùng tham số mặc định `init(analytics: AnalyticsProtocol = AnalyticsService.shared)` trong giai đoạn chuyển đổi. Trong Swift 6 language mode, `static let shared` của một class không `Sendable` còn bị compiler báo lỗi concurrency-safety (trừ khi class được isolate vào một global actor như `@MainActor`, kể cả khi điều đó được suy ra từ default actor isolation `MainActor` của Swift 6.2), buộc bạn phải nghĩ lại thiết kế.

## Bẫy phỏng vấn

### "`static let shared = NetworkManager()` có thread-safe không?"

**Dễ trả lời sai:** "Không, phải bọc bằng `dispatch_once` hoặc lock", hoặc ngược lại "có, nên cả class an toàn".

**Nên trả lời:** Swift khởi tạo `static let` một cách lazy và thread-safe (dùng `swift_once`), nên việc tạo instance chỉ xảy ra một lần. Nhưng đó chỉ là phần khởi tạo; mutable state bên trong như token hay cache vẫn bị data race nếu nhiều thread cùng đọc ghi. Swift 6 strict concurrency báo lỗi với `static var` và với `static let` có kiểu không `Sendable`; cách sửa là biến nó thành `actor`, đánh dấu `@MainActor`, hoặc bảo vệ state bằng `Mutex` (module Synchronization, iOS 18+).

### "Observer đăng ký với `NotificationCenter` thì phải `removeObserver` trong `deinit`?"

**Dễ trả lời sai:** "Luôn phải remove, không thì crash." Đây là kiến thức cũ.

**Nên trả lời:** Từ iOS 9, observer dạng selector (`addObserver(_:selector:name:object:)`) được tự huỷ đăng ký khi bị giải phóng. Bẫy thật nằm ở dạng block `addObserver(forName:object:queue:using:)`: nó trả về một token mà bạn phải giữ và tự remove, và closure capture `self` mạnh sẽ giữ object sống mãi nên `deinit` không bao giờ chạy. Với code mới, `NotificationCenter.default.notifications(named:)` dùng trong một `Task` hoặc publisher của Combine kèm `AnyCancellable` dễ quản lý vòng đời hơn.

### "Gọi `publisher.sink { ... }` mà không lưu kết quả, sao không nhận được giá trị nào?"

**Dễ trả lời sai:** "Publisher chưa phát giá trị" hoặc "do chạy sai thread".

**Nên trả lời:** `sink` trả về một `AnyCancellable`, và khi object này bị giải phóng thì subscription tự bị huỷ. Không lưu nó (compiler chỉ cảnh báo "result unused") thì subscription chết ngay sau dòng đó. Riêng publisher phát giá trị đồng bộ ngay lúc subscribe (như `Just` hay `CurrentValueSubject`) vẫn kịp giao giá trị đầu tiên trước khi bị huỷ, nên bug này thường lộ ra với giá trị đến bất đồng bộ như network response hay timer. Phải giữ lại, ví dụ `.store(in: &cancellables)` với `cancellables` là thuộc tính của object, và dùng `[weak self]` trong closure để tránh retain cycle.

## Bài tập

Refactor (trong comment/pseudocode) một singleton `NetworkManager.shared` xử lý auth token refresh, dựng request, và caching tất cả trong một class. Tách nó bằng Repository (truy cập dữ liệu theo từng resource), Strategy (retry policy có thể cắm theo từng loại endpoint), và constructor injection thay vì singleton dùng chung. Giải thích điều gì trở nên testable mà trước đó không thể.
