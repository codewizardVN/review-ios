[English](./Tasks.md) | [Tiếng Việt](./Tasks.vi.md)

[← Concurrency](./README.vi.md)

# Task và Cancellation

## Ý chính

`Task` là đơn vị công việc bất đồng bộ trong Swift Concurrency. Hiểu rõ ownership và cancellation là điều kiện cần để viết code production an toàn.

## Nội dung ôn tập

- `Task { }` — tạo một unstructured task, kế thừa actor isolation, priority và task-local values từ nơi tạo ra nó (tạo trong code `@MainActor` thì body chạy trên main actor).
- `Task.detached { }` — cũng là unstructured task nhưng không kế thừa actor, priority hay task-local; body chạy trên global executor trừ khi bạn tự `await` vào một actor.
- `Task.cancel()` — cancellation là cooperative: chỉ bật cờ, code bên trong phải tự kiểm tra `Task.isCancelled` hoặc gọi `try Task.checkCancellation()` (throw `CancellationError`).
- `withTaskCancellationHandler` — đăng ký một closure được gọi ngay lúc task bị cancel (có thể chạy song song với phần việc chính), dùng để hủy tài nguyên bên ngoài như socket hay request callback cũ.
- `TaskGroup` — fan-out nhiều child task song song; group chỉ kết thúc khi mọi child xong, và cancel group thì cancel tất cả child (structured lifecycle).

## Ví dụ

```swift
@MainActor
final class FeedViewModel: ObservableObject {
    private var loadTask: Task<Void, Never>?

    func load() {
        loadTask?.cancel()          // hủy lần load trước (nếu còn chạy)
        loadTask = Task {
            await fetchFeed()
        }
    }

    func cancel() {
        loadTask?.cancel()
    }

    private func fetchFeed() async { /* gọi API, cập nhật @Published */ }
}
```

## Câu hỏi thực hành

- Nếu người dùng rời khỏi màn hình, request đang thực thi nên được xử lý như thế nào?
- Sự khác biệt giữa `Task.detached` và `Task` thông thường là gì?

## Câu hỏi luyện tập

- Nếu user rời khỏi màn hình, request đang chạy dở nên được xử lý như thế nào?
- Sự khác biệt giữa Task.detached và một Task thông thường là gì?

## Góc nhìn Senior

Cancellation trong Swift là cooperative — bạn phải tự kiểm tra `Task.isCancelled` hoặc dùng `try Task.checkCancellation()` bên trong task body. Cancel một task không tự động dừng nó.

## Đáp án câu hỏi luyện tập

### Nếu user rời khỏi màn hình, request đang chạy dở nên được xử lý như thế nào?

Request nên bị cancel, vì kết quả không còn ai hiển thị, và việc tiếp tục chạy chỉ tốn pin, băng thông, thậm chí gây bug khi callback cập nhật một màn hình đã đóng.

Cơ chế cụ thể: trong SwiftUI, cách gọn nhất là modifier `.task { await viewModel.load() }`. Task này gắn với lifetime của view và tự cancel khi view biến mất. Trong UIKit hoặc với `FeedViewModel` như ví dụ, view model giữ `loadTask` và expose một method `cancel()`; view controller gọi nó trong `viewDidDisappear` (gọi trong `deinit` chỉ có tác dụng nếu task không giữ `self` mạnh, vì nếu giữ thì `deinit` chưa chạy cho đến khi task xong). Cancel chỉ bật một cờ; code bên trong phải tự phản ứng. May mắn là các API hệ thống như `URLSession.data(from:)` và `Task.sleep` đã kiểm tra cancellation sẵn và throw lỗi. Trong vòng lặp tự viết, bạn gọi `try Task.checkCancellation()`.

```swift
override func viewDidDisappear(_ animated: Bool) {
    super.viewDidDisappear(animated)
    viewModel.cancel()
}
```

Trade-off: không phải request nào cũng nên cancel. Một thao tác ghi như "gửi tin nhắn" hay "thanh toán" nên được hoàn thành dù user đã rời màn hình. Những việc đó nên thuộc về một service sống lâu hơn màn hình (hoặc background `URLSession`), không thuộc về view model của màn hình.

### Sự khác biệt giữa Task.detached và một Task thông thường là gì?

`Task { }` kế thừa context của nơi tạo ra nó, còn `Task.detached { }` không kế thừa gì cả.

"Context" ở đây gồm ba thứ: actor isolation (tạo trong `@MainActor` view model thì body chạy trên main actor), priority, và task-local values. Điểm chung: cả hai đều là unstructured task, nghĩa là không task nào tự động bị cancel khi scope tạo ra nó kết thúc, và bạn phải tự giữ handle để cancel.

Vì `Task { }` trong `@MainActor` chạy trên main thread, nhiều người dùng `Task.detached` để "đẩy việc nặng ra background". Việc này chạy được nhưng thường không phải lựa chọn tốt: bạn mất priority và task-local (ví dụ context tracing), và closure phải là `@Sendable` nên việc capture state trở nên khó. Cách rõ ràng hơn là đưa việc nặng vào một function `nonisolated async` hay vào một `actor` riêng, rồi `await` nó từ `Task` thường. Lưu ý phiên bản: function `nonisolated async` mặc định chạy trên global executor (Swift 5.7+); nhưng nếu project bật upcoming feature `NonisolatedNonsendingByDefault` của Swift 6.2 (có trong cài đặt "Approachable Concurrency" của Xcode 26) thì nó chạy trên actor của caller, lúc đó cần đánh dấu `@concurrent` để thật sự rời main actor. Function `nonisolated` đồng bộ (không `async`) thì luôn chạy ngay trên thread của caller.

Nên dùng `Task.detached` khi bạn thật sự muốn cắt đứt khỏi context hiện tại, ví dụ một việc dọn dẹp có priority thấp không được phép chạy trên main actor. Còn lại, mặc định chọn `Task { }` hoặc structured concurrency.

## Bẫy phỏng vấn

### "Gọi `task.cancel()` thì task dừng ngay đúng không?"

**Dễ trả lời sai:** "Đúng, cancel sẽ kill task giống như kill thread." Swift không có cơ chế dừng cưỡng bức task.

**Nên trả lời:** Cancellation là cooperative: `cancel()` chỉ đặt cờ `isCancelled` và lan truyền xuống child task. Task vẫn chạy tiếp cho đến khi code của nó kiểm tra cờ (`Task.isCancelled`, `try Task.checkCancellation()`) hoặc gọi một API có kiểm tra sẵn. Một vòng lặp tính toán đồng bộ không có điểm kiểm tra sẽ chạy đến hết dù đã bị cancel. Muốn phản ứng ngay (ví dụ đóng socket), dùng `withTaskCancellationHandler`.

### "Trong `SearchViewModel`, bắt `CancellationError` là đủ để nhận biết request bị cancel?"

**Dễ trả lời sai:** "Đủ, mọi thứ bị cancel đều throw `CancellationError`." Đây là giả định sai rất hay gặp khi làm bài tập search.

**Nên trả lời:** `URLSession` khi bị cancel throw `URLError` với code `.cancelled`, không phải `CancellationError`. Nếu chỉ `catch is CancellationError`, request bị cancel sẽ rơi vào nhánh lỗi chung và UI có thể hiện "Đã có lỗi xảy ra" cho mỗi lần gõ phím. Nên kiểm tra cả hai, hoặc đơn giản hơn là kiểm tra `Task.isCancelled` trong `catch` trước khi hiển thị lỗi.

```swift
catch where Task.isCancelled { print("cancelled") }
```

### "Dùng `[weak self]` trong `Task { }` là tránh được retain cycle?"

**Dễ trả lời sai:** "Luôn phải `[weak self]` rồi `guard let self` ở dòng đầu, như với closure thường." Viết vậy thường không giải quyết vấn đề gì.

**Nên trả lời:** `Task` giữ closure cho đến khi chạy xong, nên việc capture `self` mạnh chỉ kéo dài lifetime của `self` đến lúc task kết thúc, không phải một cycle vĩnh viễn. Còn `guard let self` ngay đầu task sẽ biến `self` thành strong reference suốt thời gian task chạy, nên `weak` gần như vô tác dụng. Vấn đề thật là task chạy vô hạn (ví dụ `for await` trên một stream không bao giờ kết thúc): khi đó task giữ `self` mạnh thì `deinit` sẽ không bao giờ chạy, nên phải cancel từ bên ngoài (`onDisappear`, `viewDidDisappear`), hoặc capture `weak` và chỉ unwrap `self` ngắn trong từng vòng lặp.

## Bài tập

Xây dựng `SearchViewModel` với method `func search(query: String)` tự cancel task search trước khi bắt đầu search mới (giữ task trong một property `task`, gọi `task?.cancel()` rồi tạo `Task { }` mới). Trong `catch`, nhận biết trường hợp bị cancel và in ra "cancelled" thay vì hiện lỗi; lưu ý `URLSession` throw `URLError(.cancelled)` chứ không phải `CancellationError`, nên dùng `catch where Task.isCancelled` hoặc kiểm tra cả hai (xem phần Bẫy phỏng vấn). Gọi `search(query:)` ba lần liên tiếp nhanh và xác nhận chỉ kết quả cuối cùng được áp dụng. Giải thích tại sao pattern này quan trọng với search field.
