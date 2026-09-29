[English](./ValueTypes.md) | [Tiếng Việt](./ValueTypes.vi.md)

[← Swift Core](./README.vi.md)

# Value Types và Reference Types

## 1. `struct` vs `class`

### Ý chính

Trong Swift, `struct` thường là lựa chọn mặc định vì nó mang lại value semantics, mutation an toàn hơn, và ít lỗi liên quan đến shared state hơn. Dùng `class` khi bạn cần identity, shared mutable state, kế thừa, hoặc hành vi lifecycle dựa trên reference.

### So sánh nhanh

- `struct`
  - Value type
  - Được sao chép khi gán hoặc truyền vào hàm (về mặt ngữ nghĩa; các kiểu như `Array`, `String` dùng copy-on-write nên dữ liệu chỉ thật sự bị copy khi có mutation)
  - An toàn hơn theo mặc định: mỗi biến giữ bản riêng, và muốn thay đổi thì biến phải là `var`, method phải là `mutating`
  - Không hỗ trợ kế thừa (dùng protocol để chia sẻ hành vi)
- `class`
  - Reference type
  - Chia sẻ cùng một instance khi gán: hai biến cùng trỏ tới một object, thay đổi qua biến này thì biến kia cũng thấy
  - Hỗ trợ kiểm tra identity bằng `===` (hai biến có trỏ tới cùng một object không)
  - Hỗ trợ kế thừa và `deinit` (struct/enum thường không có `deinit`; chỉ struct/enum `~Copyable` từ Swift 5.9 mới khai báo được `deinit`)

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

## Đáp án câu hỏi luyện tập

### Bạn sẽ dùng một kiểu BankAccount cài đặt cả dưới dạng struct lẫn class như thế nào để giải thích việc copy một struct account so với gán một class account làm thay đổi ngữ nghĩa của lời gọi transfer(to:amount:) ra sao?

Tôi sẽ cho thấy: với struct, `var copy = account` tạo ra một tài khoản độc lập nên transfer trên bản copy không đụng tới account gốc; với class, `let alias = account` chỉ thêm một reference tới cùng một object nên transfer qua `alias` làm đổi số dư mà mọi nơi đang giữ reference đều thấy.

Cơ chế nằm ở chữ ký của method. Bản struct buộc phải là `mutating` và tài khoản nhận phải là `inout`, nên call site có dấu `&` — người đọc biết ngay giá trị nào bị thay đổi. Bản class mutate cả hai object mà call site không có dấu hiệu gì.

```swift
struct AccountValue {
    var balance: Decimal
    mutating func transfer(to other: inout AccountValue, amount: Decimal) {
        balance -= amount; other.balance += amount
    }
}
var a = AccountValue(balance: 100), b = AccountValue(balance: 0)
var snapshot = a
a.transfer(to: &b, amount: 30)   // snapshot.balance vẫn là 100
```

Đánh đổi: một tài khoản ngân hàng thật có identity (có ID, là một thực thể duy nhất), nên nếu nhiều màn hình cần cùng thấy một số dư đang thay đổi thì class — hoặc tốt hơn là `actor` khi có concurrency — mô tả đúng domain hơn. Struct phù hợp để biểu diễn snapshot (số dư tại một thời điểm, dữ liệu trả về từ server), nơi việc vô tình chia sẻ state là bug chứ không phải tính năng.

## Bẫy phỏng vấn

### "Struct luôn nằm trên stack nên luôn nhanh hơn class, đúng không?"

**Dễ trả lời sai:** Đồng ý rằng struct luôn được cấp phát trên stack còn class trên heap, nên cứ đổi sang struct là nhanh hơn.

**Nên trả lời:** Vị trí lưu trữ là chi tiết implementation. Struct sẽ nằm trên heap khi nó là phần tử của `Array`, là property của một class, bị capture bởi escaping closure, hoặc quá lớn để vừa inline buffer của một existential `any P`. Một struct chứa nhiều `String`/`Array`/class reference khi copy phải retain/release từng field, có thể tốn hơn truyền một reference. Hãy chọn theo semantics, rồi đo bằng Instruments nếu nghi ngờ hiệu năng.

### "Gán một Array 1 triệu phần tử cho biến khác có copy toàn bộ dữ liệu không?"

**Dễ trả lời sai:** Có, vì Array là value type nên mỗi lần gán là copy hết dữ liệu; hoặc ngược lại, mọi struct đều tự động có copy-on-write.

**Nên trả lời:** `Array`, `Dictionary`, `Set`, `String`, `Data` dùng copy-on-write: phép gán chỉ tăng reference count của buffer bên trong, dữ liệu chỉ thật sự được copy khi một bên mutate lúc buffer không còn được tham chiếu duy nhất. Nhưng struct tự viết thì không tự có COW — nó chỉ hưởng COW từ các stored property là những kiểu trên. Muốn COW cho kiểu riêng, bạn phải tự bọc một class storage và kiểm tra `isKnownUniquelyReferenced(&storage)` trước khi mutate.

### "Struct có một property là class thì vẫn có value semantics chứ?"

**Dễ trả lời sai:** Có, vì cứ là `struct` thì copy ra là độc lập.

**Nên trả lời:** Không. Copy struct chỉ copy reference của property kiểu class, nên hai bản copy vẫn cùng trỏ tới một object và mutation trên object đó bị chia sẻ — kể cả khi struct được khai báo bằng `let`. Value semantics là thuộc tính của cả cây dữ liệu, không phải của từ khóa `struct`. Đây cũng là lý do một struct như vậy không tự động là `Sendable` trong Swift 6 nếu class bên trong không `Sendable`.

## Bài tập

Implement một kiểu `BankAccount` trước tiên là `struct`, sau đó là `class`. Thêm method `transfer(to:amount:)` để chuyển tiền giữa các tài khoản. Quan sát điều gì xảy ra khi bạn copy một struct account so với gán một class account rồi gọi transfer. Viết 3 câu giải thích khi nào mỗi lựa chọn có ý nghĩa semantic phù hợp với domain này.
