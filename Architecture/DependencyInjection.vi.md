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

## Đáp án câu hỏi luyện tập

### Dependency injection giúp ích cho việc testing như thế nào?

DI cho phép test thay dependency thật bằng fake mà test kiểm soát được, nên test chạy nhanh, ổn định và kiểm tra được cả những trường hợp khó tái hiện.

Khi `CheckoutViewModel` tự gọi `PaymentService()` và `AnalyticsService.shared`, test không có cách nào chen vào: payment gọi mạng thật, analytics gửi event thật, và state của singleton còn sót lại giữa các test. Khi dependency được truyền vào qua `init`, test tự quyết định kết quả trả về và ghi lại các lời gọi:

```swift
final class SpyAnalytics: AnalyticsProtocol {
    private(set) var events: [String] = []
    func track(_ event: String) { events.append(event) }
}

let analytics = SpyAnalytics()
let vm = CheckoutViewModel(payment: StubPayment(result: .failure(.declined)),
                           analytics: analytics)
await vm.pay()
XCTAssertTrue(analytics.events.isEmpty)
```

Lợi ích cụ thể: (1) điều khiển được đầu vào, như payment bị từ chối hay timeout, mà không cần server; (2) quan sát được đầu ra, như event nào đã được track; (3) mỗi test có object riêng, không phụ thuộc thứ tự chạy.

Trade-off: mock quá nhiều khiến test bám vào chi tiết implementation, đổi code bên trong là vỡ test dù hành vi không đổi. Chỉ fake ở ranh giới có side effect (mạng, lưu trữ, thời gian, analytics); những thứ thuần như formatter thì dùng bản thật.

### Bạn dùng tiêu chí gì để quyết định giữa DI container và inject thủ công?

Mặc định inject thủ công qua `init` và một composition root; chỉ dùng container khi chính việc nối dependency đã trở thành nỗi đau đo đếm được.

Các tiêu chí nên xem:

- **Kích thước và độ sâu của graph**: phải truyền một dependency xuyên qua bốn, năm tầng chỉ để tầng dưới cùng dùng là dấu hiệu wiring thủ công đang đắt.
- **Số scope và lifetime**: dependency theo app, theo phiên đăng nhập, theo từng flow. Quản lý nhiều scope bằng tay dễ sai.
- **Modularization**: feature module cần được dựng mà không biết concrete type từ module khác.
- **An toàn lúc compile**: DI thủ công thiếu dependency là lỗi compile. Container resolve lúc runtime như Swinject thì quên đăng ký chỉ lộ ra lúc chạy: `resolve` trả về `nil`, và vì code thường force-unwrap (`resolve(...)!`) nên kết quả là crash. Needle sinh code nên vẫn kiểm tra lúc compile, đổi lại có thêm bước build.
- **Team**: container là thêm một thứ mọi người phải học và debug.

Bước trung gian hữu ích trước khi dùng container: gom dependency của mỗi feature vào một struct `Dependencies` hoặc một factory, rồi truyền struct đó xuống. Cách này giảm việc truyền từng tham số mà vẫn giữ an toàn lúc compile.

## Bẫy phỏng vấn

### "Dùng `Container.shared.resolve(PaymentServiceProtocol.self)` bên trong class là dependency injection?"

**Dễ trả lời sai:** "Đúng, vì có dùng DI container."

**Nên trả lời:** Đó là Service Locator, gần như ngược với DI: class vẫn tự đi lấy dependency từ một global, nên nhìn `init` không biết nó cần gì, và thiếu đăng ký chỉ lộ ra lúc runtime. DI nghĩa là class nhận dependency từ bên ngoài. Container chỉ nên được gọi ở composition root để dựng object, không rải khắp code.

### "Property injection với giá trị mặc định cũng test tốt như constructor injection?"

**Dễ trả lời sai:** "Như nhau, test chỉ cần gán `vm.repository = FakeFeedRepository()`."

**Nên trả lời:** Với `var repository: FeedRepository = RemoteFeedRepository()`, bản thật đã được tạo trước khi test kịp thay; nếu `init` của nó có side effect (đọc keychain, mở kết nối), side effect vẫn xảy ra. Object cũng có thể được dùng trước khi dependency đúng được gán, và thuộc tính phải là `var` thay vì `let`, điều mà Swift 6 hay báo lỗi khi class cần `Sendable`. Constructor injection bảo đảm object luôn đầy đủ và bất biến ngay khi tạo xong.

### "`@Environment` trong SwiftUI an toàn như inject qua `init`?"

**Dễ trả lời sai:** "Như nhau, chỉ là cú pháp gọn hơn."

**Nên trả lời:** Với object `@Observable`, đọc `@Environment(CartModel.self)` mà quên gọi `.environment(cart)` ở view cha sẽ crash lúc runtime; `@EnvironmentObject` cũng vậy. Còn `EnvironmentKey` có `defaultValue` thì không crash nhưng lặng lẽ dùng giá trị mặc định, có khi là bản production trong preview hay test. Environment hợp cho dependency xuyên suốt như theme, locale; dependency bắt buộc của một màn hình nên truyền qua `init` để compiler kiểm tra.

## Bài tập

Lấy `CheckoutViewModel` gọi `PaymentService()` và `AnalyticsService.shared` bên trong. Refactor: (1) tạo `PaymentServiceProtocol` và `AnalyticsProtocol`, (2) chuyển sang constructor injection. Viết hai test: một xác nhận analytics track `"purchase_complete"` khi payment thành công, một xác nhận nó KHÔNG track khi thất bại. Giải thích tại sao constructor injection được ưu tiên hơn property injection cho required dependency.
