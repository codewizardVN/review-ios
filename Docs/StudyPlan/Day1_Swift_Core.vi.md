[English](./Day1_Swift_Core.md) | [Tiếng Việt](./Day1_Swift_Core.vi.md)

# Day 1: Swift Core

## Goal

Xây nền tảng vững cho các khái niệm Swift quan trọng nhất trong phỏng vấn Senior iOS và các quyết định thiết kế thực tế.

## Topics

- `struct` vs `class`
- Value semantics vs reference semantics
- ARC
- Retain cycle
- Protocol-oriented programming
- Generics
- Error handling
- Access control
- `any` vs `some`

## What You Should Be Able To Explain

- Khi nào `struct` là lựa chọn mặc định đúng và khi nào cần `class`
- Vì sao value semantics giúp giảm lỗi shared mutable state
- ARC hoạt động ở mức high-level như thế nào
- Retain cycle thường xuất hiện ở đâu trong code iOS
- Vì sao protocol hữu ích vượt ra ngoài chuyện abstraction
- Generic giúp cải thiện thiết kế API và type safety ra sao
- Khi nào dùng `any`, khi nào dùng `some`

## 1. `struct` vs `class`

### Ý chính

Trong Swift, `struct` thường là lựa chọn mặc định vì có value semantics, mutation an toàn hơn và ít lỗi shared state hơn. Dùng `class` khi bạn cần identity, shared mutable state, inheritance hoặc lifecycle theo reference.

### So sánh nhanh

- `struct`
  - Value type
  - Copy khi gán
  - Mặc định an toàn hơn
  - Không có inheritance
- `class`
  - Reference type
  - Chia sẻ cùng instance khi gán
  - Hỗ trợ identity checks
  - Hỗ trợ inheritance và deinit

### Ví dụ

```swift
struct UserProfile {
    var name: String
}

final class SessionManager {
    var token: String?
}
```

### Góc nhìn senior

Đừng trả lời kiểu "struct nhanh hơn, class chậm hơn". Cách đó nông và nhiều khi sai. Câu trả lời tốt hơn phải xoay quanh semantics, ownership và mutation behavior.

## 2. Value vs Reference Semantics

### Ý chính

Value type giúp giảm coupling ngoài ý muốn. Khi một phần hệ thống thay đổi dữ liệu, phần khác không tự động bị ảnh hưởng nếu bạn chưa mô hình hóa hành vi chia sẻ đó một cách tường minh.

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

Với reference type, hai biến có thể cùng trỏ vào một object và cùng mutate shared state.

### Góc nhìn senior

Điều này quan trọng trong state management, reducer, view model, cache và concurrency. Câu trả lời senior nên nối semantics với behavior của cả hệ thống.

## 3. ARC và Memory Management

### Ý chính

ARC tự động theo dõi strong references và giải phóng object khi reference count về 0.

### Điều quan trọng trong thực tế

- Strong reference giữ object sống
- Weak reference không giữ object sống
- Unowned giả định object vẫn còn tồn tại
- ARC không phải garbage collector

### Ví dụ

```swift
final class Owner {
    var child: Child?
}

final class Child {
    weak var owner: Owner?
}
```

### Góc nhìn senior

Quan trọng không phải là thuộc keyword. Quan trọng là hiểu ownership và lifecycle của object, đặc biệt qua delegate, closure, async task và quan hệ view/controller.

## 4. Retain Cycle

### Những nơi hay gặp

- Closure capture `self`
- Delegate không khai báo `weak`
- Callback sống lâu
- Timer / notification / observer
- Async work giữ object sống lâu hơn dự kiến

### Ví dụ

```swift
final class ProfileViewModel {
    var onUpdate: (() -> Void)?

    func bind() {
        onUpdate = { [weak self] in
            self?.reload()
        }
    }

    private func reload() {}
}
```

### Góc nhìn senior

Đừng dùng `[weak self]` theo quán tính ở mọi nơi. Hãy giải thích vì sao capture tồn tại, ai sở hữu ai, và có thật sự nên giữ `self` sống trong suốt operation hay không.

## 5. Protocol-Oriented Programming

### Ý chính

Protocol giúp định nghĩa contract hành vi và giảm coupling. Nó đặc biệt hữu ích cho testability, composability và boundary của API.

### Ví dụ

```swift
protocol UserRepository {
    func fetchUser(id: String) async throws -> User
}
```

### Cách nói tốt ở level senior

- Protocol hữu ích ở boundary
- Quá nhiều protocol có thể làm codebase phức tạp quá mức
- Protocol chỉ nên tồn tại khi thật sự có nhu cầu abstraction hoặc substitution

## 6. Generics

### Ý chính

Generic cho phép bạn viết API tái sử dụng được mà vẫn giữ type safety, không cần rơi về kiểu dữ liệu yếu.

### Ví dụ

```swift
struct APIResponse<T: Decodable>: Decodable {
    let data: T
}
```

### Góc nhìn senior

Câu trả lời tốt nên chỉ ra khi nào generic giúp API rõ hơn và khi nào thiết kế generic quá mức sẽ làm code khó đọc, khó maintain.

## 7. Error Handling

### Cần ôn

- `throws`
- `do-catch`
- Domain error có nghĩa
- Mapping low-level error thành lỗi có ý nghĩa với user

### Ví dụ

```swift
enum NetworkError: Error {
    case invalidResponse
    case unauthorized
    case timeout
}
```

### Góc nhìn senior

Tránh đẩy raw infrastructure error thẳng lên UI. Hãy giải thích lỗi được translate giữa các layer như thế nào.

## 8. Access Control

### Cần ôn

- `private`
- `fileprivate`
- `internal`
- `public`
- `open`

### Góc nhìn senior

Access control là chuyện thiết kế boundary và giảm misuse, không chỉ là ẩn implementation.

## 9. `any` vs `some`

### Ý chính

- `some Protocol` nghĩa là ẩn concrete type nhưng type đó cố định
- `any Protocol` nghĩa là existential storage có thể giữ bất kỳ type nào conform protocol

### Góc nhìn senior

Bạn nên hiểu đủ để bàn về thiết kế API, trade-off performance và khi nào existential type là phù hợp hơn.

## Practice Questions

- Vì sao Apple thường khuyến khích dùng `struct` nhiều trong Swift?
- Closure capture list giải quyết vấn đề gì?
- `mutating` có ý nghĩa gì với `struct`?
- `any` và `some` khác nhau thế nào?
- Khi nào dùng `weak`, khi nào dùng `unowned`?
- Khi nào protocol là hữu ích thay vì abstraction thừa?

## Mini Checklist

- Bạn có giải thích ownership rõ ràng không?
- Bạn có nhìn ra nơi shared mutable state dễ gây rủi ro không?
- Bạn có chỉ ra được nơi dễ xảy ra retain cycle không?
- Bạn có justify việc dùng `struct` hay `class` bằng trade-off thay vì mẹo nhớ không?
- Bạn có giải thích được một Swift API giữ type-safe và maintainable ra sao không?

## Suggested Exercise

Tự viết một model layer nhỏ với:

- Một `struct` entity
- Một `class` manager
- Một repository dùng protocol
- Một generic API response wrapper
- Một custom error enum

Sau đó tự giải thích vì sao chọn từng loại type.

## Senior Notes

- Đừng trả lời bằng các định nghĩa rời rạc.
- Hãy nối mọi khái niệm với ownership, maintainability, testing và behavior của hệ thống.
- Câu trả lời senior tốt thường có trade-off, không có câu khẳng định tuyệt đối.
