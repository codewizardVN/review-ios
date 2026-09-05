[English](./ErrorHandling.md) | [Tiếng Việt](./ErrorHandling.vi.md)

[← Swift Core](./README.vi.md)

# Xử lý lỗi

## Nội dung ôn tập

- `throws`
- `do-catch`
- Typed domain errors
- Ánh xạ các lỗi tầng thấp thành lỗi có ý nghĩa với người dùng

## Ví dụ

```swift
enum NetworkError: Error {
    case invalidResponse
    case unauthorized
    case timeout
}
```

## Câu hỏi luyện tập

- Một do-catch đầy đủ xử lý từng case của ParseError (missingField, invalidFormat, unsupportedVersion) với thông báo riêng cho người dùng khác gì so với việc chỉ dùng try?

## Góc nhìn Senior

Tránh để lộ các lỗi infrastructure thô trực tiếp lên UI. Hãy giải thích cách lỗi được chuyển đổi qua các layer.

## Bài tập

Định nghĩa một enum `ParseError` với các case: `missingField(String)`, `invalidFormat(String, String)`, và `unsupportedVersion(Int)`. Viết một function `parseConfig(from data: Data) throws -> Config` throw các lỗi này. Viết call site với một `do-catch` đầy đủ xử lý từng case với một thông báo riêng biệt hướng tới người dùng. Giải thích sự khác biệt so với việc chỉ dùng `try?`.
