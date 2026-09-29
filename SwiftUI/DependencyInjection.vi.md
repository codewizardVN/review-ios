[English](./DependencyInjection.md) | [Tiếng Việt](./DependencyInjection.vi.md)

[← SwiftUI](./README.vi.md)

# Dependency Injection trong SwiftUI

## Ý chính

SwiftUI hoạt động tốt nhất khi dependency được thể hiện tường minh. View nên nhận dữ liệu và service nó cần qua initializer, environment value, hoặc state object mà ownership được xác định rõ.

## Cách tiếp cận phổ biến

### Initializer injection

Tốt cho dependency rõ ràng và preview dễ dựng. View (hoặc view model) nhận dependency qua tham số `init`, nên chỉ cần nhìn signature là biết nó cần gì, và compiler bắt lỗi nếu quên truyền. Nhược điểm: phải truyền qua từng tầng view nếu dependency nằm sâu.

### Environment injection

Hữu ích cho dependency dùng xuyên suốt app, nhưng có thể trở nên quá ngầm nếu lạm dụng. Ancestor đặt giá trị bằng `.environment(...)` (custom key khai báo bằng `@Entry` trong `extension EnvironmentValues`, hoặc object `@Observable` theo type), view con cháu đọc bằng `@Environment` mà không cần tham số. Tiện, nhưng dependency không hiện trong signature của view.

### `@StateObject` ownership

Phù hợp khi view tạo và sở hữu một view model, còn view model đó lại phụ thuộc vào các service được truyền vào. Thường viết `init(repository: UserRepository) { _viewModel = StateObject(wrappedValue: ProfileViewModel(repository: repository)) }` (hoặc `_viewModel = State(initialValue: ...)` với `@Observable`); lưu ý giá trị này chỉ được dùng ở lần đầu cho mỗi identity của view.

## Câu hỏi thực hành

- Khi nào `EnvironmentObject` hữu ích, khi nào quá "ma thuật"?
- Làm sao giữ SwiftUI preview dễ dựng?

## Câu hỏi luyện tập

- Khi nào EnvironmentObject hữu ích so với khi nào nó quá "magic"?
- Làm sao bạn giữ cho SwiftUI preview dễ dựng?

## Góc nhìn senior

Mục tiêu không phải loại bỏ mọi convenience. Mục tiêu là giữ ownership và chiều của dependency đủ rõ để view tree vẫn testable và predictable.

## Đáp án câu hỏi luyện tập

### Khi nào EnvironmentObject hữu ích so với khi nào nó quá "magic"?

`EnvironmentObject` hữu ích khi dependency thực sự xuyên suốt app và sống theo app hoặc scene — session, theme, feature flags, router — còn nó trở nên quá "magic" khi được dùng để truyền những dependency riêng của một màn hình, khiến không ai nhìn vào view mà biết nó cần gì.

Cơ chế: ancestor inject một object theo type, view con cháu đọc lại theo type mà không cần tham số trong initializer. Điều này tiết kiệm việc "khoan" dependency qua năm sáu tầng view, nhưng đổi lại:

- Signature của view không phản ánh dependency, nên preview, test và người đọc code phải tự đoán.
- Thiếu inject là crash lúc runtime, không có kiểm tra lúc compile.
- Mỗi type chỉ có một instance trong một nhánh cây, khó có hai phiên bản song song.

Quy tắc thực tế: nếu dependency cần ở nhiều màn không liên quan và có một instance duy nhất cho cả app, environment là hợp lý. Nếu chỉ `ProfileView` và view model của nó cần `UserRepository`, hãy truyền qua initializer. Từ iOS 17, `@Environment(Session.self)` với `@Observable` thay thế `EnvironmentObject`, nhưng câu hỏi "có nên dùng environment không" vẫn trả lời theo cùng tiêu chí.

### Làm sao bạn giữ cho SwiftUI preview dễ dựng?

Giữ preview dễ dựng bằng cách để mọi dependency đi qua protocol và được truyền từ ngoài vào, để preview chỉ cần một dòng khởi tạo với mock thay vì cả app.

Cụ thể:

- Định nghĩa `UserRepository` là protocol; có một bản mock trả dữ liệu mẫu ngay lập tức.
- View model nhận repository qua `init`; view nhận view model (hoặc repository) qua `init`.
- View không tự gọi `.shared` hay singleton bên trong `body`/`init`.
- Chuẩn bị sẵn dữ liệu mẫu (`Profile.sample`) cho các trạng thái loading, rỗng, lỗi.

```swift
struct MockUserRepository: UserRepository {
    func fetchProfile() async throws -> Profile { .sample }
}

#Preview {
    ProfileView(viewModel: ProfileViewModel(repository: MockUserRepository()))
}
```

Với dependency đi qua environment, hãy cho environment key một default an toàn (no-op hoặc mock) thay vì service thật, hoặc dùng `PreviewModifier` (iOS 18+) để dựng một lần môi trường chung cho nhiều preview. Trade-off: protocol cho mọi thứ tạo thêm boilerplate; chỉ trừu tượng hóa những dependency có side effect (network, database, clock), không phải mọi struct đơn giản.

## Bẫy phỏng vấn

### "Lấy service từ @Environment rồi truyền vào @StateObject ngay trong init của view?"

**Dễ trả lời sai:** Viết `init() { _viewModel = StateObject(wrappedValue: ProfileViewModel(repository: repository)) }` với `repository` là một `@Environment` property, và nghĩ rằng nó sẽ hoạt động.

**Nên trả lời:** Giá trị `@Environment` chỉ hợp lệ khi view đã được gắn vào cây và `body` đang chạy; trong `init`, nó chưa có giá trị đúng (SwiftUI còn log cảnh báo khi đọc environment ngoài view). Cách đúng: tách một view wrapper đọc environment trong `body` rồi truyền xuống `init` của view con, hoặc cấu hình view model trong `.task { viewModel.configure(repository) }`.

### "Dùng singleton static let shared cho session là cách DI đơn giản nhất?"

**Dễ trả lời sai:** Cho rằng `SessionManager.shared` gọi từ khắp nơi cũng chấp nhận được, chỉ là "ít đẹp" hơn.

**Nên trả lời:** Singleton ẩn dependency: test không thay được, preview gọi luôn service thật. Trong Swift 6 language mode, `static let shared = SessionManager()` với class không `Sendable` và không bị cô lập vào actor nào còn là lỗi compile ("static property 'shared' is not concurrency-safe..."), buộc bạn phải đánh dấu `@MainActor`, biến nó thành actor, hoặc làm cho type `Sendable`. (Project mới tạo bằng Xcode 26 thường bật default actor isolation `MainActor`, khi đó type ngầm định là `@MainActor` nên lỗi này không xuất hiện — nhưng vấn đề dependency bị ẩn vẫn còn.) Có thể giữ một instance duy nhất ở composition root, nhưng hãy inject nó chứ đừng để view tự với tới.

### "Default value của environment key là nơi hợp lý để đặt service thật?"

**Dễ trả lời sai:** Khai báo `@Entry var userRepository: any UserRepository = LiveUserRepository()` để khỏi phải inject ở root.

**Nên trả lời:** Default sẽ được dùng mỗi khi bạn quên inject, nên preview và test âm thầm gọi network thật, và lỗi quên inject không bao giờ lộ ra (khác với `@EnvironmentObject`, thiếu inject ở đây không crash). Ngoài ra macro `@Entry` sinh `defaultValue` của key dưới dạng static computed property (`static var defaultValue: Value { LiveUserRepository() }`), nên mỗi khi SwiftUI cần tới giá trị default (không có ancestor nào inject), biểu thức default có thể được đánh giá lại và tạo instance mới — với reference type, các view khác nhau có thể nhận các instance khác nhau chứ không phải một instance dùng chung như tưởng. Tần suất chính xác SwiftUI đọc default không được tài liệu hóa, nên đừng dựa vào nó. Hãy để default là no-op hoặc placeholder, và inject bản live một lần ở root của app.

## Bài tập

Thiết kế `ProfileView` phụ thuộc vào `UserRepository`. Hãy viết một phiên bản dùng initializer injection vào view model và một phiên bản dùng environment injection. Sau đó giải thích cách nào bạn ưu tiên cho một session dependency dùng chung toàn app.
