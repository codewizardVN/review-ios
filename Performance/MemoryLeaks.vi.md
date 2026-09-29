[English](./MemoryLeaks.md) | [Tiếng Việt](./MemoryLeaks.vi.md)

[← Performance](./README.vi.md)

# Memory Leaks và Retain Cycles

## Tìm kiếm Leak

1. **Instruments → Leaks** — phát hiện memory đã được cấp phát nhưng không còn được tham chiếu từ bất kỳ root nào (global, stack, register), ví dụ hai object giữ nhau trong một retain cycle mà không ai khác trỏ tới. Object bị giữ "hợp lệ" (bởi run loop, singleton, cache) thì Leaks không báo — xem Bẫy phỏng vấn
2. **Memory Graph Debugger** — dừng app trong Xcode, click nút memory graph để hiển thị tất cả object đang sống và đường dẫn tham chiếu của chúng
3. **`deinit` logging** — thêm `print("deinit \(Self.self)")` trong quá trình phát triển để xác minh object được giải phóng

## Nguồn gốc phổ biến trong iOS

- Observer dạng block (`addObserver(forName:object:queue:using:)`): notification center giữ closure, closure capture `self` mạnh — nếu chỉ định remove observer trong `deinit` thì `deinit` không bao giờ chạy. (Observer dạng selector từ iOS 9 không bị giữ strong và không cần tự remove.)
- Delegate property không có `weak`: A giữ B, B giữ lại A qua delegate → cycle
- `Timer`: run loop giữ timer, timer giữ target (API target/selector) hoặc closure của nó — nếu closure capture `self` mạnh thì view controller sống mãi cho tới khi timer bị `invalidate()`
- `Task { }` capture `self` và chạy rất lâu (vòng lặp `for await` vô hạn, polling): `self` bị giữ cho tới khi task kết thúc

## Ví dụ

```swift
// Leak: Timer retain self mạnh
class BadViewController: UIViewController {
    var timer: Timer?
    override func viewDidLoad() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            self.update() // strong capture
        }
    }
}

// Đã sửa: weak capture + invalidate khi rời màn hình
override func viewDidAppear(_ animated: Bool) {
    super.viewDidAppear(animated)
    timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
        // Swift 6: closure của Timer là @Sendable; timer được lên lịch trên
        // main run loop nên dùng assumeIsolated để gọi method @MainActor
        MainActor.assumeIsolated { self?.update() }
    }
}

override func viewDidDisappear(_ animated: Bool) {
    super.viewDidDisappear(animated)
    timer?.invalidate() // run loop thả timer, timer ngừng fire
    timer = nil
}
```

## Câu hỏi luyện tập

- Nếu deinit của một view controller không bao giờ được gọi sau khi navigate away vì một Timer hoặc NotificationCenter observer, bạn sẽ dùng Memory Graph Debugger như thế nào để tìm và sửa retain cycle?

## Góc nhìn senior

Leak trong production thường tinh tế — không phải trong closure rõ ràng mà trong observer chain, analytics hook, hoặc background task sống lâu hơn màn hình. Dùng Memory Graph trong QA, không chỉ trong development.

## Đáp án câu hỏi luyện tập

### Nếu deinit của một view controller không bao giờ được gọi sau khi navigate away vì một Timer hoặc NotificationCenter observer, bạn sẽ dùng Memory Graph Debugger như thế nào để tìm và sửa retain cycle?

Mở Memory Graph Debugger ngay sau khi đã rời màn hình, tìm instance view controller vẫn còn sống, rồi lần theo các strong reference trỏ vào nó để biết ai đang giữ nó. Các bước cụ thể:

- Trước khi chạy, bật Scheme → Diagnostics → Malloc Stack Logging (Live Allocations Only) để Xcode ghi lại backtrace nơi mỗi object được cấp phát.
- Mở rồi đóng màn hình vài lần, sau đó bấm nút Debug Memory Graph trên thanh debug.
- Gõ tên class vào ô filter ở navigator bên trái. Mở 3 lần mà còn 3 instance thì chắc chắn có vấn đề.
- Chọn một instance: graph ở giữa hiển thị các object trỏ tới nó, đường đậm là strong reference. Với Timer thường thấy chuỗi `NSRunLoop → __NSCFTimer → closure → ViewController`; với observer dạng block là `NSNotificationCenter → observer → closure → ViewController`.
- Inspector bên phải hiển thị backtrace lúc closure được tạo, dẫn thẳng về dòng code gây lỗi.

Cách sửa: capture `[weak self]` trong closure, và quan trọng hơn là chấm dứt nguồn đang giữ: gọi `timer?.invalidate()` khi màn hình biến mất (ví dụ `viewDidDisappear`), gọi `NotificationCenter.default.removeObserver(token)` với observer dạng block. Chạy lại và xác nhận `deinit` được in ra.

Lưu ý: trường hợp này thường không bị đánh dấu là "leak" (dấu "!" tím), vì view controller vẫn reachable từ run loop hoặc notification center. Vì vậy phải tự phát hiện bằng cách đếm số instance, không chờ công cụ cảnh báo.

## Bẫy phỏng vấn

### "Thêm `[weak self]` vào closure của Timer là xong rồi phải không?"

**Dễ trả lời sai:** `[weak self]` phá retain cycle nên không cần làm gì thêm với Timer.

**Nên trả lời:** `[weak self]` giúp view controller được giải phóng, nhưng run loop vẫn giữ timer, nên timer tiếp tục fire mãi với `self` là `nil` — tốn CPU và pin. Phải `invalidate()` timer khi màn hình biến mất. Với API `Timer.scheduledTimer(timeInterval:target:selector:...)`, timer giữ target strong và `[weak self]` không áp dụng được; gọi `invalidate()` trong `deinit` là vô dụng vì `deinit` sẽ không bao giờ chạy khi timer còn giữ `self`.

### "Instruments Leaks không báo gì, vậy app không leak?"

**Dễ trả lời sai:** Leaks instrument sạch nghĩa là không có memory bị giữ sai.

**Nên trả lời:** Leaks chỉ tìm memory không còn reachable từ root nào. Object bị giữ bởi run loop, singleton, cache hay notification center vẫn reachable nên không bị báo — đây là abandoned memory, loại phổ biến nhất trong app thật. Dùng Allocations với Mark Generation: đánh dấu, mở/đóng màn hình, đánh dấu lại; memory tăng đều qua mỗi generation là dấu hiệu object bị giữ lại.

### "Trong `Task { }` dùng `[weak self]` rồi `guard let self` ở đầu là an toàn?"

**Dễ trả lời sai:** Đã capture weak nên task không bao giờ giữ `self`.

**Nên trả lời:** `guard let self` ở đầu tạo một strong reference tồn tại suốt thời gian task chạy. Với task ngắn thì không sao — `self` được thả khi task xong, và đó cũng là lý do một `Task` ngắn thường không cần `[weak self]`. Nhưng với vòng lặp dài như `for await note in NotificationCenter.default.notifications(named:)`, `self` bị giữ vô thời hạn. Cách đúng: lưu handle và `cancel()` task khi màn hình biến mất (SwiftUI `.task` tự cancel), hoặc chỉ unwrap `self` bên trong từng vòng lặp.

## Bài tập

Thêm `deinit { print("deinit \(Self.self)") }` vào ViewController dùng `Timer` và `NotificationCenter` observer. Navigate đi và xác nhận deinit được gọi. Nếu không, dùng Memory Graph Debugger để tìm retain cycle và sửa.
