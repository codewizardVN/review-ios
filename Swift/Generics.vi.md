[English](./Generics.md) | [Tiếng Việt](./Generics.vi.md)

[← Swift Core](./README.vi.md)

# Generics

## Ý chính

Generics cho phép bạn viết các API có thể tái sử dụng và type-safe mà không cần dùng đến weakly typed code (như `Any` rồi ép kiểu bằng `as!`). Bạn viết code một lần với một type parameter (ví dụ `T`), và mỗi nơi sử dụng sẽ điền vào một kiểu cụ thể; compiler kiểm tra kiểu ngay lúc compile nên không có lỗi ép kiểu lúc runtime. Constraint như `T: Decodable` giới hạn những kiểu được phép và cho biết bạn được dùng thao tác nào trên `T`.

## Ví dụ

```swift
struct APIResponse<T: Decodable>: Decodable {
    let data: T
}
```

## Câu hỏi luyện tập

- Tại sao constraint Equatable lại cần thiết cho method contains(_:) của EquatableStack, điều mà một Stack<Element> generic thông thường không thể hỗ trợ?

## Góc nhìn Senior

Một câu trả lời cấp Senior tốt giải thích khi nào generics cải thiện sự rõ ràng của API và khi nào thiết kế generic nặng nề trở nên khó đọc và khó bảo trì.

## Đáp án câu hỏi luyện tập

### Tại sao constraint Equatable lại cần thiết cho method contains(_:) của EquatableStack, điều mà một Stack<Element> generic thông thường không thể hỗ trợ?

Vì `contains(_:)` phải so sánh phần tử bằng `==`, mà với một `Element` không có constraint thì compiler không biết gì về kiểu đó nên không cho phép gọi `==`.

Cơ chế: Swift type-check code generic một lần tại nơi định nghĩa, không phải cho từng kiểu cụ thể như C++ template. Bên trong `Stack<Element>`, compiler chỉ cho dùng những thao tác mà mọi `Element` có thể có — lưu, trả về, copy. `Element` có thể là một closure `() -> Void`, và closure không so sánh được. Khi viết `Element: Equatable`, bạn đưa ra một lời hứa mà compiler kiểm tra tại chỗ sử dụng: `EquatableStack<Int>` hợp lệ, còn `EquatableStack<() -> Void>` báo lỗi compile.

Đánh đổi: tạo hẳn một kiểu `EquatableStack` riêng là lặp code, và một stack chứa `Int` phải chọn giữa hai kiểu. Cách Swift thường dùng là conditional extension, giống cách `Array` (qua `Sequence`) chỉ có `contains(_:)` khi `Element: Equatable`. Ví dụ dưới giả định `Stack` lưu phần tử trong `private var items: [Element]` và extension nằm cùng file (nên truy cập được `private`):

```swift
extension Stack where Element: Equatable {
    func contains(_ element: Element) -> Bool {
        items.contains(element)
    }
}
```

Như vậy `Stack<Int>` có `contains`, còn `Stack<() -> Void>` vẫn dùng được, chỉ là không có method này. Nếu cần so sánh theo tiêu chí khác, thêm `contains(where:)` nhận predicate.

## Bẫy phỏng vấn

### "Generics trong Swift giống C++ template, luôn được specialize nên không tốn chi phí gì?"

**Dễ trả lời sai:** Đúng, compiler sinh ra một bản code riêng cho mỗi kiểu cụ thể, nên generic luôn nhanh như code viết tay.

**Nên trả lời:** Specialization chỉ là một tối ưu hóa, không được đảm bảo. Code generic có thể chạy ở dạng không specialize, truyền type metadata và witness table lúc runtime — thường gặp khi gọi qua ranh giới module mà hàm không được đánh dấu `@inlinable`, và ở build Debug (`-Onone`) thì gần như không specialize. Trong cùng module với optimization bật (Release), compiler thường specialize được. Đây cũng là lý do Swift type-check generic tại nơi định nghĩa: code phải đúng cho mọi kiểu thỏa constraint.

### "Box<Cat> có dùng được ở chỗ cần Box<Animal> không, nếu Cat là subclass của Animal?"

**Dễ trả lời sai:** Có, vì `[Cat]` truyền được vào chỗ cần `[Animal]` nên kiểu generic nào cũng vậy.

**Nên trả lời:** Không. Generic tự viết trong Swift là invariant: `Box<Cat>` và `Box<Animal>` là hai kiểu không liên quan. `Array`, `Optional`, `Dictionary`, `Set` được compiler xử lý đặc biệt để có covariance (và một số conversion, ví dụ `[Cat]` sang `[any P]`, phải tạo mảng mới). Với kiểu của bạn, phải tự chuyển đổi, ví dụ `let animalBox = Box<Animal>(value: catBox.value)`.

### "Trong hàm generic, gọi một hàm có overload cho Int thì có chạy overload Int khi T là Int không?"

**Dễ trả lời sai:** Có, Swift chọn overload phù hợp nhất theo kiểu thực tế lúc runtime.

**Nên trả lời:** Không. Overload được chọn lúc compile dựa trên những gì compiler biết về `T` tại chỗ gọi. Trong `func log<T>(_ x: T) { describe(x) }`, compiler chỉ biết `T` là "một kiểu bất kỳ", nên luôn gọi `describe<T>(_:)` chung, kể cả khi truyền vào `Int` và có `describe(_: Int)`. Muốn hành vi thay đổi theo kiểu thì dùng protocol requirement (dispatch qua witness table), không dùng overload.

## Bài tập

Implement một generic `Stack<Element>` với `push(_:)`, `pop() -> Element?`, và `peek() -> Element?`. Thêm một phiên bản thứ hai `EquatableStack<Element: Equatable>` có thêm method `contains(_ element: Element) -> Bool`. Viết 3 ví dụ sử dụng cho thấy tại sao generic constraint trên phiên bản thứ hai là cần thiết.
