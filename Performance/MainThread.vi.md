[English](./MainThread.md) | [Tiếng Việt](./MainThread.vi.md)

[← Performance](./README.vi.md)

# Main Thread Discipline

## Ý tưởng chính

Main thread chịu trách nhiệm cho tất cả cập nhật UI: xử lý touch, layout, vẽ và commit frame. Nếu một đoạn code chiếm main thread lâu hơn thời gian của một frame (khoảng 16,7ms ở 60Hz, 8,3ms ở 120Hz), frame đó bị trễ và người dùng thấy giật (hitch/jank); nếu bị chặn khoảng từ 250ms trở lên thì hệ thống coi là hang. Vì vậy công việc nặng không liên quan đến UI (decode, I/O, tính toán lớn) nên được chuyển ra khỏi main thread; công việc nhỏ thì không cần — chi phí chuyển thread có thể lớn hơn chính công việc.

## Các vi phạm phổ biến

- Decode JSON trên main thread sau khi nhận network response (response lớn có thể mất hàng chục ms)
- Fetch từ Core Data đồng bộ trên main thread (ví dụ fetch hàng nghìn object bằng `viewContext`), hoặc đọc/ghi file đồng bộ
- Decode (giải nén) ảnh trên main thread — UIKit mặc định decode ảnh "lười" ngay lúc ảnh được hiển thị lần đầu
- Tính toán nặng trong `body` hoặc `cellForItemAt` — các hàm này được gọi rất nhiều lần khi scroll hoặc khi state đổi

## Phát hiện

- Xcode: Main Thread Checker (bật mặc định khi Run từ Xcode) — lưu ý nó bắt lỗi *gọi UI API từ background thread*, không đo main thread bị block (xem Bẫy phỏng vấn)
- Instruments: Time Profiler (lọc theo main thread, tìm stack chạy lâu), Hangs và Animation Hitches để thấy main thread bị chặn ở đâu
- Assertion trong code: `dispatchPrecondition(condition: .onQueue(.main))` hoặc `MainActor.assertIsolated()`; `Thread.isMainThread` vẫn dùng được trong code đồng bộ, nhưng ở Swift 6 nó không được phép gọi trong ngữ cảnh `async`

## Ví dụ sửa lỗi

```swift
// Sai: decode trên main thread
func didReceiveData(_ data: Data) {
    let items = try? JSONDecoder().decode([Item].self, from: data) // blocks main
    self.items = items
}

// Đúng: decode ngoài main, cập nhật trên main
// (giả định class là @MainActor, Item là Sendable)
func didReceiveData(_ data: Data) {
    Task.detached {
        let items = try? JSONDecoder().decode([Item].self, from: data)
        await MainActor.run { self.items = items }
    }
}
```

## Câu hỏi luyện tập

- Tại sao việc decode JSON và filter kết quả của SearchViewModel phải chuyển ra khỏi main thread bằng Task.detached, rồi publish kết quả về trên @MainActor, thay vì làm trực tiếp trong didReceiveData?

## Góc nhìn senior

`@MainActor` trên ViewModel có nghĩa là các property và method của nó chạy trên main actor (tức main thread). Mọi đoạn code *đồng bộ* trong một method `@MainActor` — kể cả phần nằm giữa các `await` — đều chạy trên main, nên decode nặng đặt ở đó vẫn block UI. Điều `await` mang lại là: khi method bị suspend để chờ, main actor được giải phóng để làm việc khác (xử lý touch, render). Còn hàm được `await` chạy ở đâu là do isolation của chính hàm đó quyết định: hàm của một actor khác chạy trên actor đó, hàm `@concurrent` (hoặc `nonisolated async` khi chưa bật `NonisolatedNonsendingByDefault`) chạy trên global concurrent executor, còn `URLSession.data(for:)` thì chờ I/O mà không chiếm thread nào. Khi hàm đó xong, phần còn lại của method tiếp tục trên main. Vì vậy mẫu đúng là: giữ ViewModel `@MainActor`, đẩy công việc CPU nặng vào một hàm được đánh dấu rõ là chạy ngoài main, rồi `await` kết quả.

## Đáp án câu hỏi luyện tập

### Tại sao việc decode JSON và filter kết quả của SearchViewModel phải chuyển ra khỏi main thread bằng Task.detached, rồi publish kết quả về trên @MainActor, thay vì làm trực tiếp trong didReceiveData?

Vì decode và filter một response lớn là công việc CPU thuần, có thể mất hàng chục đến hàng trăm millisecond, trong khi main thread chỉ có khoảng 8–16ms cho mỗi frame. Nếu `didReceiveData` làm việc này trên main thread, main thread bị chiếm trọn cho tới khi xong: không xử lý touch, không layout, không commit frame mới — người dùng thấy scroll khựng hoặc gõ phím bị trễ. `Task.detached` tạo một task không kế thừa actor của nơi gọi, nên phần thân chạy trên cooperative thread pool (background). Khi có kết quả, ta quay về `@MainActor` để gán `items`, vì state mà UI đọc chỉ được thay đổi trên main thread (UIKit/SwiftUI không thread-safe, và Swift 6 báo lỗi compile nếu vi phạm isolation).

```swift
func didReceiveData(_ data: Data, query: String) {
    searchTask?.cancel()
    searchTask = Task.detached(priority: .userInitiated) { [weak self] in
        let all = (try? JSONDecoder().decode([Item].self, from: data)) ?? []
        let hits = all.filter { $0.title.localizedCaseInsensitiveContains(query) }
        guard !Task.isCancelled else { return }
        await self?.apply(hits) // apply là method @MainActor
    }
}
```

Trade-off: `Task.detached` không kế thừa priority, task-local value và cancellation của task cha, nên phải tự giữ handle để cancel khi query mới đến (tránh kết quả cũ ghi đè kết quả mới). `Item` phải `Sendable`. Với dữ liệu nhỏ (vài KB), chi phí nhảy thread có thể lớn hơn chính công việc — đo bằng Time Profiler trước. Một cách gọn hơn `Task.detached` là tách logic ra một hàm async chạy ngoài main rồi `await` nó từ ViewModel. Trước Swift 6.2, hàm `nonisolated async` luôn chạy trên global executor (background). Từ Swift 6.2, nếu bật `NonisolatedNonsendingByDefault` (mặc định trong project mới tạo bằng Xcode 26 qua build setting Approachable Concurrency), hàm `nonisolated async` chạy trên actor của caller — tức vẫn là main nếu gọi từ ViewModel — nên phải đánh dấu `@concurrent` để chắc chắn chạy nền. Đánh dấu `@concurrent` cũng đúng khi chưa bật cờ đó, nên với Swift 6.2+ đó là cách ghi rõ ý định an toàn nhất.

## Bẫy phỏng vấn

### "Viết `Task { }` bên trong ViewModel `@MainActor` là đã chạy ở background rồi, đúng không?"

**Dễ trả lời sai:** Cứ bọc code vào `Task { }` là nó chạy trên thread khác, nên decode JSON bên trong `Task { }` sẽ không block UI.

**Nên trả lời:** `Task { }` kế thừa actor isolation của ngữ cảnh tạo ra nó, nên trong một class `@MainActor` closure vẫn chạy trên main actor. Code đồng bộ bên trong (decode, filter) vẫn chiếm main thread; `Task` chỉ hoãn nó sang lượt chạy sau chứ không đổi thread. Muốn rời main phải dùng `Task.detached`, hoặc `await` một hàm `@concurrent` (hoặc `nonisolated async` nếu project chưa bật `NonisolatedNonsendingByDefault` — xem bẫy tiếp theo).

### "Hàm decode đã là `async` rồi, vậy chắc chắn nó không chạy trên main?"

**Dễ trả lời sai:** Đánh dấu `async` là hàm tự động chạy nền.

**Nên trả lời:** `async` chỉ nói hàm có thể suspend, không quyết định hàm chạy ở đâu. Hàm async thuộc `@MainActor` (ví dụ method của ViewModel) chạy trên main. Với hàm `nonisolated async`, hành vi phụ thuộc phiên bản: trước Swift 6.2 nó chạy trên global executor (background); từ Swift 6.2, nếu bật `NonisolatedNonsendingByDefault` (thường qua build setting Approachable Concurrency trong Xcode 26), nó chạy trên actor của caller — tức vẫn là main nếu gọi từ main; nếu không bật cờ này thì hành vi cũ vẫn giữ nguyên, kể cả với Swift 6.2. Muốn chắc chắn chạy nền bất kể cấu hình thì đánh dấu `@concurrent` (Swift 6.2+). Cũng lưu ý: dù hàm chạy trên background, nếu bên trong nó chỉ là code đồng bộ dài thì nó vẫn chiếm một thread của cooperative pool suốt thời gian đó.

### "Main Thread Checker không báo gì, vậy main thread ổn chứ?"

**Dễ trả lời sai:** Main Thread Checker không báo lỗi nghĩa là không có vấn đề hiệu năng trên main thread.

**Nên trả lời:** Main Thread Checker phát hiện chiều ngược lại: gọi API UIKit/AppKit từ background thread. Nó không đo việc main thread bị block lâu. Để tìm công việc nặng trên main, dùng Instruments (Time Profiler, Hangs, Animation Hitches), Thread Performance Checker của Xcode (báo priority inversion và công việc không phải UI trên main), và dữ liệu hang từ Xcode Organizer/MetricKit ở production.

## Bài tập

Bạn có `SearchViewModel` decode JSON response lớn và filter kết quả trên main thread trong `didReceiveData`. Refactor để decode và filter trên background thread dùng `Task.detached`, sau đó publish kết quả về trên `@MainActor`. Xác minh tính đúng đắn với Main Thread Checker (không có cảnh báo UI API bị gọi từ background), và xác minh hiệu quả bằng Time Profiler hoặc Hangs trong Instruments (main thread không còn stack decode/filter dài).
