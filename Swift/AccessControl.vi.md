[English](./AccessControl.md) | [Tiếng Việt](./AccessControl.vi.md)

[← Swift Core](./README.vi.md)

# Access Control

## Nội dung ôn tập

- `private` — chỉ hiển thị trong phạm vi khai báo bao quanh và các extension của nó trong cùng file
- `fileprivate` — hiển thị trong cùng source file
- `internal` — hiển thị trong module (mặc định)
- `public` — hiển thị bên ngoài module, nhưng không thể subclass/override
- `open` — hiển thị bên ngoài module và có thể subclass/override

## Câu hỏi luyện tập

- Bạn sẽ thiết kế struct KeychainStore với các access level phù hợp cho items được lưu trữ, các method public read/write, và helper encrypt nội bộ như thế nào, và điều gì sẽ hỏng nếu items là public?

## Góc nhìn Senior

Access control là về API boundaries và giảm thiểu việc sử dụng sai, không chỉ đơn thuần là ẩn chi tiết implementation.

## Bài tập

Thiết kế một struct `KeychainStore` lưu trữ `private var items: [String: String]`. Expose một `public func read(key: String) -> String?` và một `public mutating func write(key: String, value: String)`. Giữ `private func encrypt(_ value: String) -> String` ở phạm vi nội bộ. Viết comment cho từng access level giải thích quyết định thiết kế. Giải thích điều gì sẽ bị phá vỡ nếu `items` là public.
