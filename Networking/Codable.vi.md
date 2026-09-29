[English](./Codable.md) | [Tiếng Việt](./Codable.vi.md)

[← Networking](./README.vi.md)

# Codable

## Ý chính

`Codable` (`Encodable + Decodable`) cung cấp JSON serialization type-safe mà không cần parse thủ công.

## Nội dung ôn tập

- `CodingKeys` — enum `String, CodingKey` khai báo tên key trong JSON cho từng property (ví dụ `displayName = "display_name"`); property nào không có trong `CodingKeys` sẽ không được decode/encode (khi đó nó phải có giá trị mặc định).
- Custom `init(from:)` — tự viết decode khi JSON phức tạp hoặc không chuẩn: object lồng nhau cần "làm phẳng", field có thể là số hoặc chuỗi, cần default khi thiếu key (`decodeIfPresent(...) ?? default`).
- Cấu hình `JSONDecoder` — `keyDecodingStrategy` (ví dụ `.convertFromSnakeCase` tự đổi `display_name` thành `displayName`), `dateDecodingStrategy` (mặc định là `.deferredToDate`, tức số giây kể từ 2001-01-01, nên với chuỗi ngày ISO 8601 phải đặt `.iso8601` hoặc `.custom`).
- DTOs vs domain models — decode vào DTO (khớp đúng hình dạng JSON) rồi map sang domain type (khớp cách app dùng dữ liệu).

## Ví dụ

```swift
// Decoder cần: decoder.dateDecodingStrategy = .iso8601 để đọc "created_at" dạng chuỗi ISO 8601
struct UserDTO: Decodable {
    let id: String
    let displayName: String
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case displayName = "display_name"
        case createdAt = "created_at"
    }
}
```

## Câu hỏi luyện tập

- Điều gì sẽ hỏng nếu domain model User decode JSON trực tiếp thay vì đi qua UserDTO với CodingKeys mapping và chuyển đổi toDomain()?

## Góc nhìn Senior

Không decode trực tiếp vào domain model. Giữ DTO riêng biệt — API contract và domain model phải có thể phát triển độc lập. Map tại ranh giới data layer giữ domain sạch.

## Đáp án câu hỏi luyện tập

### Điều gì sẽ hỏng nếu domain model User decode JSON trực tiếp thay vì đi qua UserDTO với CodingKeys mapping và chuyển đổi toDomain()?

Domain model `User` sẽ bị trói chặt vào API contract: mỗi khi backend đổi tên key, đổi format ngày hay đổi nullability, lỗi decode lan thẳng vào domain và mọi màn hình đang dùng `User`.

Cụ thể những thứ hỏng:
- **Tên property bị ép theo API.** `User` phải mang `CodingKeys` kiểu `"user_id"`, `"joined_at"`; muốn đặt tên theo ngôn ngữ của domain là phải đụng vào decoding.
- **Nullability rò vào domain.** API trả `display_name` có thể null thì `User` phải có `String?`, và mọi chỗ dùng đều phải unwrap, dù về nghiệp vụ user luôn có tên hiển thị (có thể fallback).
- **Không có chỗ để validate và chuẩn hóa.** `toDomain()` là nơi tự nhiên để trim chuỗi, gán default, chuyển `String` sang `URL`, hoặc loại bỏ dữ liệu invalid. Decode thẳng thì chỉ có hai kết quả: thành công hoặc throw.
- **Endpoint khác trả shape khác** (ví dụ `/me` có thêm field) buộc domain model phải chiều theo cả hai.
- **Test và persistence bị kéo theo**: mock JSON và dữ liệu cache phải khớp đúng wire format.

Trade-off: DTO thêm một type và một hàm mapping cho mỗi entity. Với app nhỏ, payload do chính team kiểm soát và khớp y hệt domain, decode trực tiếp vẫn chấp nhận được — nhưng tách ra về sau luôn tốn hơn làm ngay từ đầu.

## Bẫy phỏng vấn

### Dùng `keyDecodingStrategy = .convertFromSnakeCase` cùng lúc với `CodingKeys` có raw value `"display_name"` thì sao?

**Dễ trả lời sai:** "Không sao, strategy chỉ là fallback, `CodingKeys` sẽ được ưu tiên."

**Nên trả lời:** `JSONDecoder` chuyển key trong JSON sang camelCase trước (`display_name` thành `displayName`), rồi mới so với raw value của `CodingKeys`. Vì raw value vẫn là `"display_name"` nên không khớp, và decode ném `keyNotFound`. Chỉ chọn một trong hai: dùng strategy và để `CodingKeys` theo camelCase, hoặc bỏ strategy và map tay. Thêm một bẫy nhỏ: `user_id` được chuyển thành `userId`, không phải `userID`.

### `dateDecodingStrategy = .iso8601` có decode được mọi chuỗi ISO 8601 không?

**Dễ trả lời sai:** "Có, backend gửi ISO 8601 thì `.iso8601` là đủ."

**Nên trả lời:** `.iso8601` không nhận phần giây lẻ, nên `"2024-03-15T10:00:00.123Z"` sẽ fail và làm hỏng cả payload. Nếu backend có thể gửi fractional seconds, dùng `.custom` với `Date.ISO8601FormatStyle(includingFractionalSeconds: true)` và thử cả hai format. Tốt nhất là chốt format với backend và viết test decode bằng chuỗi thật lấy từ API.

### Property `var isVerified: Bool = false` có được dùng giá trị mặc định khi JSON thiếu key không?

**Dễ trả lời sai:** "Có, Swift sẽ dùng giá trị mặc định nếu key không tồn tại."

**Nên trả lời:** Với `Decodable` do compiler synthesize, giá trị mặc định của `var` bị bỏ qua: nó vẫn gọi `decode(Bool.self, forKey:)`, nên thiếu key là throw `keyNotFound`. Chỉ property `Optional` mới được decode bằng `decodeIfPresent` (thiếu key hoặc `null` đều ra `nil`). Muốn có default thật thì viết `init(from:)` với `decodeIfPresent(...) ?? false`, hoặc để DTO dùng Optional rồi gán default trong `toDomain()`. Cũng vì cơ chế này mà một phần tử lỗi làm cả mảng `[UserDTO]` decode thất bại.

## Bài tập

Với JSON `{"user_id":"u1","display_name":"Alice","joined_at":"2024-03-15T10:00:00Z"}`, viết `UserDTO` với `CodingKeys` map snake_case keys. Viết `User` domain model với property name khác. Thêm `toDomain() -> User`. Cấu hình `JSONDecoder` với `.iso8601` date strategy. Giải thích trong comment điều gì hỏng nếu domain model decode JSON trực tiếp.
