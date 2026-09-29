[English](./RequestResponseMapping.md) | [Tiếng Việt](./RequestResponseMapping.vi.md)

[← Data và Networking](./README.vi.md)

# Mapping Request và Response

## Ý chính

Hãy tách kiểu dữ liệu của transport layer khỏi domain layer. Request và response nên phản ánh contract của API, còn domain model nên phản ánh hành vi của app.

## Vì sao quan trọng

- Field từ API thường có tên hoặc nullability không phù hợp trực tiếp với UI
- Domain model nên ổn định ngay cả khi payload backend thay đổi
- Mapping là nơi phù hợp để chuẩn hóa default và translate raw error

## Ví dụ

```swift
struct UserDTO: Decodable {
    let id: String
    let fullName: String
    let avatarURL: URL?
}

struct User {
    let id: String
    let displayName: String
    let avatarURL: URL?
}

extension UserDTO {
    func toDomain() -> User {
        User(id: id, displayName: fullName, avatarURL: avatarURL)
    }
}
```

## Câu hỏi thực hành

- Khi nào có thể chấp nhận bỏ qua DTO?
- Mapping nên nằm ở đâu: service, repository, hay use case?

## Câu hỏi luyện tập

- Khi nào việc bỏ qua DTO là chấp nhận được?
- Việc mapping nên nằm ở đâu: service, repository, hay use case?

## Góc nhìn senior

Mapping không phải việc thừa. Nó tạo ra boundary để bảo vệ UI và domain khỏi biến động từ backend. Chỉ nên bỏ boundary này khi app còn nhỏ và shape của payload đã thật sự khớp với behavior của sản phẩm.

## Đáp án câu hỏi luyện tập

### Khi nào việc bỏ qua DTO là chấp nhận được?

Có thể bỏ qua DTO khi payload thực sự đã khớp với cách app dùng dữ liệu và chi phí thay đổi về sau thấp.

Những trường hợp thường gặp:
- **App nhỏ, prototype hoặc tính năng thử nghiệm**, khi tốc độ ra sản phẩm quan trọng hơn độ ổn định lâu dài.
- **Backend do chính team kiểm soát**, đặc biệt là BFF (backend-for-frontend) được thiết kế theo đúng màn hình của app, nên tên field và nullability đã đúng ý domain.
- **Dữ liệu đơn giản, chỉ đọc**, như config hay feature flag, không có logic nghiệp vụ.
- **Type chỉ dùng bên trong data layer**, không bao giờ đi ra tới UI.

Điều kiện để bỏ qua an toàn: decoding vẫn nằm ở một chỗ duy nhất (repository hoặc API client), để ngày backend thay đổi bạn chỉ cần chèn DTO vào đó mà không phải sửa ViewModel hay View. Ngược lại, không nên bỏ DTO khi API là của bên thứ ba, payload có nhiều field optional hoặc tên xấu, nhiều endpoint trả cùng một entity với shape khác nhau, hoặc dữ liệu cần validate trước khi dùng — như `FeedItemDTO` với `image_url` có thể thiếu hoặc sai định dạng.

Trade-off: DTO tốn thêm code nhưng mua được sự độc lập giữa API và domain; bỏ DTO tiết kiệm lúc đầu nhưng biến mỗi thay đổi backend thành một thay đổi lan rộng khắp app.

### Việc mapping nên nằm ở đâu: service, repository, hay use case?

Thường nên đặt mapping ở repository (tầng data), vì đó chính là ranh giới giữa "dữ liệu đến từ một nguồn nào đó" và "domain model mà phần còn lại của app dùng".

Phân vai dễ hiểu:
- **Service / API client** chỉ lo transport: build request, gửi, kiểm tra status, decode ra DTO. Nó không cần biết domain.
- **Repository** gọi service (và có thể cả cache hay database), rồi gọi `toDomain()` để trả về `FeedItem`. Vì repository có thể trộn nhiều nguồn, nó là nơi duy nhất cần biết mỗi nguồn trả về shape gì.
- **Use case** chỉ làm việc với domain model và luật nghiệp vụ. Nếu use case nhận DTO, domain lại phụ thuộc vào API — đúng thứ ta muốn tránh.

Còn một loại mapping thứ hai: từ domain sang dữ liệu hiển thị (format ngày theo locale, ghép chuỗi "bởi \(author)"). Phần này thuộc presentation — ViewModel hoặc một formatter — chứ không phải repository.

Trade-off: với app nhỏ không có tầng use case, mapping trong service vẫn chấp nhận được, miễn là DTO không lọt ra khỏi data layer. Đặt mapping trong use case chỉ hợp lý khi một use case phải gộp nhiều DTO đặc thù — hiếm gặp, và thường là dấu hiệu repository đang thiếu một method.

## Bẫy phỏng vấn

### `toDomain()` có nên luôn trả về giá trị, không bao giờ fail?

**Dễ trả lời sai:** "Có, mapping chỉ là copy field, field nào thiếu thì gán default."

**Nên trả lời:** Mapping là nơi quyết định chính sách với dữ liệu xấu, và câu trả lời khác nhau theo từng field. Field bắt buộc (như `id`, hoặc `created_at` không parse được) thì `toDomain()` nên throw hoặc trả `nil`, rồi repository dùng `compactMap` để bỏ item đó và log lại, thay vì làm hỏng cả feed. Field phụ (như `image_url`) thì map thành `nil` và UI hiển thị placeholder. Gán default bừa (ví dụ `Date()` cho ngày tạo bị lỗi) sẽ âm thầm tạo ra dữ liệu sai. Lưu ý thêm: nếu DTO khai báo `image_url` là `URL?`, thì `null` hoặc thiếu key cho ra `nil`, nhưng một chuỗi không tạo được `URL` (ví dụ chuỗi rỗng `""`) sẽ làm decode throw và hỏng cả item. Muốn "sai định dạng thì coi như không có ảnh", hãy để DTO giữ `String?` rồi chuyển bằng `URL(string:)` trong `toDomain()`.

### Có nên format `created_at` thành chuỗi "2 giờ trước" ngay trong `toDomain()`?

**Dễ trả lời sai:** "Nên, để UI chỉ việc hiển thị."

**Nên trả lời:** Domain nên giữ `Date`, vì chuỗi hiển thị phụ thuộc locale, timezone và thời điểm hiện tại — "2 giờ trước" sẽ sai sau một tiếng. Format là việc của presentation (ViewModel, `FormatStyle`, hoặc `Text(date, style: .relative)`). Nếu domain chỉ giữ chuỗi, bạn mất khả năng sort, so sánh và test theo thời gian.

### Để `URLError` và `DecodingError` đi thẳng lên ViewModel có sao không?

**Dễ trả lời sai:** "Không sao, ViewModel tự `switch` trên error để hiển thị thông báo."

**Nên trả lời:** Như vậy ViewModel phụ thuộc vào chi tiết transport và decoding, và mỗi lần đổi cách gọi network là phải sửa UI. Tầng data nên dịch lỗi thô sang lỗi domain có ý nghĩa như `.offline`, `.unauthorized`, `.notFound`, `.invalidData`, để ViewModel chỉ quyết định cách hiển thị. Vẫn nên giữ lỗi gốc trong log hoặc associated value để debug.

## Bài tập

Thiết kế `FeedItemDTO` trả về từ API với `created_at`, `author_name`, và `image_url` optional. Map nó sang domain `FeedItem` dùng cho UI. Sau đó giải thích bạn sẽ xử lý field thiếu hoặc invalid ở đâu.
