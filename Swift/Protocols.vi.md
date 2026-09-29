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

- Protocol hữu ích tại các ranh giới (boundaries): giữa ViewModel và tầng network/storage, giữa module này và module khác — nơi bạn muốn thay implementation (bản thật, bản test, bản offline) mà không sửa code gọi.
- Quá nhiều protocol có thể làm codebase trở nên phức tạp không cần thiết: mỗi protocol là một lớp gián tiếp, người đọc phải nhảy qua lại giữa protocol và implementation.
- Protocol nên tồn tại khi có nhu cầu substitution (thay thế implementation, ví dụ để test) hoặc abstraction (nhiều kiểu thật sự chia sẻ một hành vi) thực sự, không phải "vì POP nói vậy".

## Câu hỏi luyện tập

- Tại sao việc inject protocol AnalyticsService (với FirebaseAnalytics và NoOpAnalytics) vào initializer của CheckoutViewModel lại giúp ViewModel có thể test được?

## Đáp án câu hỏi luyện tập

### Tại sao việc inject protocol AnalyticsService (với FirebaseAnalytics và NoOpAnalytics) vào initializer của CheckoutViewModel lại giúp ViewModel có thể test được?

Vì `CheckoutViewModel` chỉ phụ thuộc vào một contract chứ không phụ thuộc vào Firebase, nên trong test ta có thể truyền vào một implementation khác không gọi SDK, không cần mạng, không gửi event thật, và kết quả luôn giống nhau mỗi lần chạy.

Cơ chế: nếu ViewModel tự tạo `FirebaseAnalytics()` bên trong, test không có cách nào thay nó. Khi dependency đi qua initializer, người tạo ViewModel quyết định dùng implementation nào: app dùng `FirebaseAnalytics`, test dùng `NoOpAnalytics`. Lưu ý `NoOpAnalytics` chỉ giúp test logic khác mà không bị side effect; muốn kiểm tra "bấm thanh toán thì có track đúng event" thì cần một spy ghi lại event.

```swift
final class CheckoutViewModel {
    private let analytics: any AnalyticsService
    init(analytics: any AnalyticsService) { self.analytics = analytics }
    func pay() { analytics.track(event: "checkout_pay") }
}

final class SpyAnalytics: AnalyticsService {
    private(set) var events: [String] = []
    func track(event: String) { events.append(event) }
}
```

Đánh đổi: mỗi protocol là một lớp gián tiếp mà người đọc phải lần theo. Chỉ tạo protocol ở những ranh giới có side effect thật (network, analytics, storage, thời gian). Với Swift 6, nếu ViewModel là `@MainActor` và service được dùng từ nhiều nơi, bạn còn phải nghĩ tới việc protocol có cần `Sendable` hay không.

## Bẫy phỏng vấn

### "Method trong protocol extension được gọi qua any P sẽ chạy bản nào?"

**Dễ trả lời sai:** Luôn chạy bản của conforming type vì Swift dùng dynamic dispatch giống override của class.

**Nên trả lời:** Còn tùy method đó có phải là requirement hay không. Nếu method được khai báo trong protocol thì gọi qua witness table, chạy bản của conforming type. Nếu method chỉ nằm trong extension mà không có trong khai báo protocol, nó được dispatch tĩnh theo kiểu tĩnh của biến: gọi qua `any AnalyticsService` sẽ luôn chạy bản trong extension, kể cả khi `FirebaseAnalytics` có method cùng tên. Muốn "override" được thì phải đưa method vào khai báo protocol.

### "Protocol có associatedtype thì không dùng làm kiểu biến được đúng không?"

**Dễ trả lời sai:** Đúng, vẫn gặp lỗi "can only be used as a generic constraint", phải dùng type erasure như `AnyPublisher` cho mọi trường hợp.

**Nên trả lời:** Đó là kiến thức trước Swift 5.7. Từ Swift 5.7, SE-0309 cho phép khai báo `any Collection` (existential cho protocol có associated type/`Self`), và SE-0346 (primary associated type) cho phép viết `any Collection<Int>` hoặc `some Collection<Int>`. Tuy vậy, qua một existential bạn không gọi được method nhận associated type hoặc `Self` làm tham số (vì compiler không biết kiểu cụ thể bên trong); lúc đó cần truyền existential vào một hàm generic (Swift 5.7 tự "mở" existential, SE-0352) hoặc dùng type erasure thủ công. Type erasure như `AnyPublisher` vẫn hữu ích để giấu kiểu cụ thể trong API, nhưng không còn là cách duy nhất.

### "Mỗi class nên có một protocol để dễ mock, đúng không?"

**Dễ trả lời sai:** Đúng, POP nghĩa là tạo protocol cho mọi service/manager, mỗi cái đi kèm một mock.

**Nên trả lời:** Protocol chỉ có một implementation thật và một mock thường chỉ là thêm lớp gián tiếp: khó "jump to definition", dễ lệch giữa protocol và class. Hãy tạo protocol ở ranh giới có side effect hoặc có nhiều implementation thật. Với dependency nhỏ, truyền một closure (`track: (String) -> Void`) hoặc một struct chứa closure thường đơn giản hơn mà vẫn test được.

## Bài tập

Định nghĩa một protocol `AnalyticsService` với một method duy nhất `track(event: String)`. Viết hai conforming type: `FirebaseAnalytics` (chỉ in "Firebase: \(event)") và `NoOpAnalytics` (không làm gì). Inject `AnalyticsService` vào `CheckoutViewModel` thông qua initializer của nó. Viết một unit test sử dụng `NoOpAnalytics`. Giải thích tại sao protocol boundary giúp ViewModel có thể test được.
