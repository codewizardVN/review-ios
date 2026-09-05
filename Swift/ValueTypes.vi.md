[English](./ValueTypes.md) | [Tiếng Việt](./ValueTypes.vi.md)

[← Swift Core](./README.vi.md)

# Value Types và Reference Types

## 1. `struct` vs `class`

### Ý chính

Trong Swift, `struct` thường là lựa chọn mặc định vì nó mang lại value semantics, mutation an toàn hơn, và ít lỗi liên quan đến shared state hơn. Dùng `class` khi bạn cần identity, shared mutable state, kế thừa, hoặc hành vi lifecycle dựa trên reference.

### So sánh nhanh

- `struct`
  - Value type
  - Được sao chép khi gán
  - An toàn hơn theo mặc định
  - Không hỗ trợ kế thừa
- `class`
  - Reference type
  - Chia sẻ cùng một instance khi gán
  - Hỗ trợ kiểm tra identity
  - Hỗ trợ kế thừa và deinitialization

### Ví dụ

```swift
struct UserProfile {
    var name: String
}

final class SessionManager {
    var token: String?
}
```

### Góc nhìn Senior

Đừng trả lời câu hỏi này theo kiểu "struct nhanh hơn, class chậm hơn". Câu trả lời đó nông cạn và thường sai. Câu trả lời tốt hơn phải nói về semantics, ownership, và hành vi mutation.

---

## 2. Value Semantics vs Reference Semantics

### Ý chính

Value types giảm thiểu việc vô tình tạo ra sự phụ thuộc lẫn nhau. Khi một phần của hệ thống thay đổi một giá trị, phần khác sẽ không âm thầm nhận thấy cùng một sự thay đổi đó trừ khi bạn mô hình hóa hành vi đó một cách tường minh.

### Ví dụ

```swift
struct Counter {
    var value: Int
}

var a = Counter(value: 0)
var b = a
b.value = 10

print(a.value) // 0
print(b.value) // 10
```

Với reference type, cả hai biến có thể trỏ đến cùng một object và thay đổi shared state.

### Góc nhìn Senior

Điều này quan trọng trong state management, reducers, view models, caching, và concurrency. Một câu trả lời cấp Senior phải kết nối semantics với hành vi của hệ thống.

## Câu hỏi luyện tập

- Bạn sẽ dùng một kiểu BankAccount cài đặt cả dưới dạng struct lẫn class như thế nào để giải thích việc copy một struct account so với gán một class account làm thay đổi ngữ nghĩa của lời gọi transfer(to:amount:) ra sao?

## Bài tập

Implement một kiểu `BankAccount` trước tiên là `struct`, sau đó là `class`. Thêm method `transfer(to:amount:)` để chuyển tiền giữa các tài khoản. Quan sát điều gì xảy ra khi bạn copy một struct account so với gán một class account rồi gọi transfer. Viết 3 câu giải thích khi nào mỗi lựa chọn có ý nghĩa semantic phù hợp với domain này.
