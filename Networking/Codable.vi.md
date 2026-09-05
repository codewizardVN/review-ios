[English](./Codable.md) | [Tiếng Việt](./Codable.vi.md)

[← Networking](./README.vi.md)

# Codable

## Ý chính

`Codable` (`Encodable + Decodable`) cung cấp JSON serialization type-safe mà không cần parse thủ công.

## Nội dung ôn tập

- `CodingKeys` — map JSON key sang Swift property name
- Custom `init(from:)` — xử lý cấu trúc JSON phức tạp hoặc không chuẩn
- Cấu hình `JSONDecoder` — `keyDecodingStrategy`, `dateDecodingStrategy`
- DTOs vs domain models — decode vào DTO rồi map sang domain type

## Ví dụ

```swift
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

## Bài tập

Với JSON `{"user_id":"u1","display_name":"Alice","joined_at":"2024-03-15T10:00:00Z"}`, viết `UserDTO` với `CodingKeys` map snake_case keys. Viết `User` domain model với property name khác. Thêm `toDomain() -> User`. Cấu hình `JSONDecoder` với `.iso8601` date strategy. Giải thích trong comment điều gì hỏng nếu domain model decode JSON trực tiếp.
