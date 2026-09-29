[English](./OpaqueTypes.md) | [Tiếng Việt](./OpaqueTypes.vi.md)

[← Swift Core](./README.vi.md)

# Opaque Types: `any` vs `some`

## Ý chính

- `some Protocol` (opaque type, có từ Swift 5.1 ở vị trí return) — kiểu cụ thể được ẩn đi nhưng cố định tại compile time. Ở vị trí return, chính hàm (callee) chọn kiểu và giấu tên nó khỏi caller, nên còn được gọi là "reverse generics". Compiler vẫn biết kiểu thật, nên không cần "hộp" existential.
- `any Protocol` (existential, từ khóa `any` có từ Swift 5.6) — một "hộp" có thể chứa bất kỳ conforming type nào, và kiểu bên trong có thể thay đổi lúc runtime (ví dụ mảng chứa nhiều kiểu khác nhau). Đổi lại phải dispatch động qua witness table và có thể cấp phát heap. Lưu ý: Swift 6 language mode vẫn chưa bắt buộc viết `any` (có thể bật bắt buộc bằng upcoming feature `ExistentialAny`), nhưng nên viết rõ để người đọc biết đây là existential.

## Ví dụ

```swift
// some: caller không biết kiểu cụ thể, nhưng nó cố định
func makeView() -> some View { ... }

// any: có thể chứa bất kỳ conforming type nào — linh hoạt hơn, hiệu năng thấp hơn
var repo: any UserRepository
```

## Câu hỏi luyện tập

- Tại sao some Shape phù hợp cho một factory function như makeDefaultShape() nhưng any Shape lại cần thiết cho một function như largestShape(from shapes: [any Shape])?

## Góc nhìn Senior

Bạn cần hiểu đủ sâu để thảo luận về API design, các đánh đổi về hiệu năng, và khi nào existential type là lựa chọn phù hợp hơn.

## Đáp án câu hỏi luyện tập

### Tại sao some Shape phù hợp cho một factory function như makeDefaultShape() nhưng any Shape lại cần thiết cho một function như largestShape(from shapes: [any Shape])?

Vì `makeDefaultShape()` luôn trả về đúng một kiểu cụ thể (`Circle`), còn `largestShape` phải làm việc với một mảng trộn lẫn `Circle` và `Rectangle`, và kết quả trả về là kiểu nào thì chỉ biết lúc runtime.

Cơ chế: `some Shape` ở vị trí return nghĩa là "một kiểu cụ thể duy nhất mà caller không cần biết tên". Compiler vẫn biết đó là `Circle`, nên không cần boxing vào existential và compiler có thể tối ưu (dispatch tĩnh, specialize) như với kiểu cụ thể, và sau này bạn có thể đổi sang kiểu khác mà không phá code của caller. Nhưng mọi nhánh return phải cùng một kiểu — `if big { Circle() } else { Rectangle() }` sẽ lỗi compile.

`any Shape` là một existential: một "hộp" chứa giá trị (inline nếu nhỏ, trên heap nếu lớn) cùng type metadata và witness table, nên mỗi phần tử của mảng có thể là một kiểu khác nhau. Nếu viết `[some Shape]` ở tham số, nó tương đương một generic `<S: Shape>` và `[S]` — mọi phần tử phải cùng một kiểu. Kết quả của `largestShape` cũng phụ thuộc dữ liệu, nên chỉ có thể là `any Shape`.

Đánh đổi: `any` tốn thêm chi phí (hộp, dispatch động, có thể cấp phát heap) và làm mất thông tin kiểu. Nếu mảng luôn đồng nhất, generic `func largest<S: Shape>(from shapes: [S]) -> S` vừa nhanh hơn vừa giữ được kiểu cụ thể cho caller.

## Bẫy phỏng vấn

### "some View và any View khác nhau gì, chẳng phải chỉ là hai cách viết?"

**Dễ trả lời sai:** Chỉ là cú pháp khác nhau; trong `body` trả về `Text` ở nhánh này và `Image` ở nhánh kia vẫn được, nên `some` cũng linh hoạt như `any`.

**Nên trả lời:** `some View` là một kiểu cố định lúc compile, compiler biết chính xác nó là gì. `body` trả về được nhiều loại view trong `if/else` là nhờ `@ViewBuilder` (requirement `body` trong protocol `View` được đánh dấu `@ViewBuilder`, nên `body` của bạn tự có nó) gói chúng thành một kiểu duy nhất `_ConditionalContent<Text, Image>`, không phải nhờ `some`. Một function thường trả về `some View` không có `@ViewBuilder` mà có hai nhánh khác kiểu sẽ lỗi compile. Dùng `AnyView` (type erasure) thì làm SwiftUI mất thông tin kiểu để diff hiệu quả.

### "some ở vị trí tham số nghĩa là gì?"

**Dễ trả lời sai:** Nghĩa giống ở vị trí return: callee chọn kiểu và giấu đi; hoặc cho rằng nó giống `any`.

**Nên trả lời:** Từ Swift 5.7 (SE-0341), `func draw(_ s: some Shape)` chỉ là cách viết ngắn của `func draw<S: Shape>(_ s: S)`. Ở tham số, caller mới là người chọn kiểu, và đây là generic được dispatch tĩnh, không phải existential. Vì vậy `some` ở return là "reverse generics" (callee chọn), còn ở tham số là generic bình thường (caller chọn).

### "any Shape có conform tới Shape không?"

**Dễ trả lời sai:** Có, nên `[any Shape]` truyền được vào mọi hàm generic `<S: Shape>(_: [S])`, và `any Equatable` so sánh được bằng `==`.

**Nên trả lời:** Nói chung existential không tự conform tới protocol của nó (ngoại lệ: `any Error` conform `Error`, và một số `@objc` protocol). Từ Swift 5.7 (SE-0352), một giá trị `any Shape` đơn lẻ được "mở" ngầm khi truyền vào tham số `some Shape` hoặc `<S: Shape>(_: S)`, nên trường hợp đơn giản chạy được. Nhưng `[any Shape]` không truyền được vào `[S]`, và `any Equatable` không dùng `==` với nhau được vì hai giá trị có thể là hai kiểu khác nhau.

## Bài tập

Viết một protocol `Shape` với property `var area: Double`. Tạo hai conforming type: `Circle` và `Rectangle`. Viết một function `makeDefaultShape() -> some Shape` trả về một `Circle`. Sau đó viết một function `largestShape(from shapes: [any Shape]) -> any Shape`. Giải thích trong comment tại sao `some` phù hợp cho factory function nhưng `any` lại cần thiết cho tham số array.
