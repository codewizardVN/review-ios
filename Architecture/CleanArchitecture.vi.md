[English](./CleanArchitecture.md) | [Tiếng Việt](./CleanArchitecture.vi.md)

[← Architecture](./README.vi.md)

# Clean Architecture

## Ý chính

Tổ chức code thành các tầng đồng tâm nơi dependency chỉ trỏ vào trong. Các tầng bên trong không biết gì về tầng bên ngoài.

## Các tầng (ngoài → trong)

1. **Presentation** — ViewModels, Views, UI logic
2. **Domain** — Use Cases, Entities, Repository protocols
3. **Data** — Repository implementations, API clients, local storage

Lưu ý: danh sách trên không phải ba vòng lồng nhau theo thứ tự. Domain là tầng trong cùng; Presentation và Data đều là tầng ngoài, nằm hai bên và cùng trỏ vào Domain (xem sơ đồ bên dưới).

## Quy tắc phụ thuộc

Domain layer không được phụ thuộc vào các chi tiết hay thay đổi: UIKit/SwiftUI, networking (`URLSession`), framework lưu trữ (Core Data, SwiftData) hay SDK bên thứ ba. Dùng các value type nền tảng của Foundation như `Date`, `UUID`, `Decimal` là bình thường (xem phần Bẫy phỏng vấn). Domain chỉ định nghĩa entity, use case và protocol; các tầng ngoài implement những protocol đó.

```text
Presentation → Domain ← Data
```

## Ví dụ

```swift
// Domain layer — pure Swift, no UIKit
protocol UserRepository {
    func fetchUser(id: String) async throws -> User
}

struct FetchUserUseCase {
    let repository: UserRepository
    func execute(id: String) async throws -> User {
        try await repository.fetchUser(id: id)
    }
}

// Data layer — implements the protocol
final class RemoteUserRepository: UserRepository {
    func fetchUser(id: String) async throws -> User { ... }
}
```

## Câu hỏi thực hành

- App nhỏ có nên dùng Clean Architecture không?
- Khi nào Clean Architecture trở thành over-engineering?

## Câu hỏi luyện tập

- Một app nhỏ có nên dùng Clean Architecture không?
- Khi nào Clean Architecture trở thành over-engineering?

## Góc nhìn Senior

Giá trị của Clean Architecture nằm ở testability và replaceability — bạn có thể swap data layer mà không động đến domain. Chi phí là boilerplate và indirection. Nó có giá trị với team lớn, domain phức tạp, hoặc app cần test nhiều.

## Đáp án câu hỏi luyện tập

### Một app nhỏ có nên dùng Clean Architecture không?

Thường là không nên dựng đủ bộ ba tầng với use case cho từng hành động, nhưng nên giữ ý tưởng cốt lõi của nó: dependency trỏ vào trong và có protocol ở ranh giới với network, database.

Giá trị của Clean Architecture đến từ việc cách ly business logic khỏi những chi tiết hay thay đổi (API, framework lưu trữ, UI). App nhỏ thường có rất ít business logic: phần lớn là lấy dữ liệu từ server rồi hiển thị. Khi đó `FetchUserUseCase` chỉ gọi lại `repository.fetchUser(id:)`, còn DTO, Entity và model hiển thị gần như giống hệt nhau. Bạn trả chi phí (thêm file, thêm mapper, thêm protocol) mà không nhận lại gì.

Cách thực tế cho app nhỏ: MVVM cộng một repository protocol như `UserRepository`. Chừng đó đã đủ để fake dữ liệu trong test và preview. Khi một business rule thật sự xuất hiện, hoặc logic cần dùng lại ở nhiều màn hình, lúc đó mới thêm use case.

Ngoại lệ: app nhỏ nhưng domain phức tạp và sống lâu (tính lãi suất, bảo hiểm, y tế), hoặc team biết chắc app sẽ lớn nhanh và cần chuẩn chung từ đầu. Khi đó đầu tư sớm là hợp lý.

### Khi nào Clean Architecture trở thành over-engineering?

Nó thành over-engineering khi các tầng trung gian không mua được gì: không thêm khả năng test, không giúp thay thế, không giúp team làm song song.

Dấu hiệu cụ thể:

- Use case chỉ có một dòng forward sang repository, và hầu như use case nào cũng như vậy.
- Ba model giống hệt nhau (DTO, Entity, UI model) với mapper chỉ copy từng field.
- Thêm một field hiển thị phải sửa sáu, bảy file qua mọi tầng.
- Mỗi use case có một protocol riêng chỉ để mock, dù test có thể dùng use case thật với fake repository.
- Tách mỗi tầng thành một module riêng cho app năm màn hình.
- Người mới vào team mất nhiều ngày chỉ để hiểu một luồng đơn giản đi qua đâu.

Nguyên tắc: mỗi lớp indirection phải trả lời được câu "nó bảo vệ mình khỏi thay đổi nào?". Nếu không trả lời được, gộp tầng lại nhưng vẫn giữ quy tắc phụ thuộc, ví dụ ViewModel gọi repository protocol trực tiếp. Bạn giữ được testability mà bỏ được phần lớn boilerplate.

## Bẫy phỏng vấn

### "Domain layer có được `import Foundation` không?"

**Dễ trả lời sai:** "Không, domain phải là Swift thuần tuyệt đối, không được dùng `Date`, `URL` hay `Decimal`." Cách hiểu này khiến team tự viết lại kiểu dữ liệu cơ bản mà không được lợi gì.

**Nên trả lời:** Quy tắc phụ thuộc nhằm tránh phụ thuộc vào chi tiết hay thay đổi: `URLSession`, Core Data, `UIImage`, SDK bên thứ ba. Các value type của Foundation như `Date`, `UUID`, `Decimal` là nền tảng ổn định, dùng trong domain là bình thường. Vì `import Foundation` trên nền tảng Apple cũng mở ra `URLSession`, compiler không tự chặn được; muốn ép thật thì đặt domain vào một target/module riêng không phụ thuộc module networking.

### "`Presentation → Domain ← Data` nghĩa là dữ liệu chạy từ Data về Domain, đúng không?"

**Dễ trả lời sai:** Nhầm hướng dependency trong source code với hướng control flow lúc runtime.

**Nên trả lời:** Lúc runtime, lời gọi đi Presentation → Use case → `RemoteUserRepository` (tầng Data). Nhưng trong source code, Data phụ thuộc vào Domain vì nó implement protocol `UserRepository` do Domain định nghĩa. Đây là Dependency Inversion: Domain sở hữu interface, tầng ngoài cung cấp implementation. Việc nối concrete type với protocol diễn ra ở composition root (app target hoặc `SceneDelegate`).

### "`FetchUserUseCase` là struct nên tự động `Sendable`, truyền qua actor thoải mái?"

**Dễ trả lời sai:** "Struct là value type nên luôn an toàn khi chạy concurrency."

**Nên trả lời:** Struct chỉ được suy ra `Sendable` khi mọi stored property đều `Sendable`, và việc suy ra ngầm này chỉ áp dụng cho struct không `public` (struct `public` phải tự khai báo `: Sendable`, trừ struct `@frozen`). Ở đây `repository` có kiểu `any UserRepository`, không `Sendable` trừ khi protocol khai báo `protocol UserRepository: Sendable`. Trong Swift 6 strict concurrency, chia sẻ use case này qua ranh giới isolation sẽ báo lỗi, ví dụ capture nó trong một `Task` rồi vẫn tiếp tục dùng ở bên ngoài, hay truyền vào một actor khác. Region-based isolation (SE-0414, Swift 6) chỉ cho phép "chuyển giao" một giá trị non-`Sendable` khi phía gửi không còn dùng nó nữa, nên đừng dựa vào đó cho một dependency dùng chung. Cách sửa là cho protocol kế thừa `Sendable` và bảo đảm implementation thật sự an toàn (immutable, actor, hoặc có khoá).

## Bài tập

Implement tính năng "Get article list" theo 3 tầng: (1) Domain: `Article` entity, `ArticleRepository` protocol, `GetArticlesUseCase`. (2) Data: `RemoteArticleRepository` gọi URLSession, trong test được stub bằng một `URLProtocol` tuỳ biến (hoặc inject một `HTTPClient` protocol). (3) Presentation: `ArticleListViewModel` dùng `GetArticlesUseCase`. Wire chúng trong unit test — không có network thật. Xác nhận domain layer không có UIKit hay networking imports.
