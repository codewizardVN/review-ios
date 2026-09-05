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

## Bài tập

Thiết kế `FeedItemDTO` trả về từ API với `created_at`, `author_name`, và `image_url` optional. Map nó sang domain `FeedItem` dùng cho UI. Sau đó giải thích bạn sẽ xử lý field thiếu hoặc invalid ở đâu.
