[English](./MemoryLeaks.md) | [Tiếng Việt](./MemoryLeaks.vi.md)

[← Performance](./README.vi.md)

# Memory Leaks và Retain Cycles

## Tìm kiếm Leak

1. **Instruments → Leaks** — phát hiện object được cấp phát nhưng không bao giờ được giải phóng
2. **Memory Graph Debugger** — dừng app trong Xcode, click nút memory graph để hiển thị tất cả object đang sống và đường dẫn tham chiếu của chúng
3. **`deinit` logging** — thêm `print("deinit \(Self.self)")` trong quá trình phát triển để xác minh object được giải phóng

## Nguồn gốc phổ biến trong iOS

- Closure trong `NotificationCenter` không được remove khi `deinit`
- Delegate property không có `weak`
- `Timer` giữ strong reference đến target
- `Task { }` capture `self` mạnh qua vòng đời dài

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

// Đã sửa
timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
    self?.update()
}
```

## Góc nhìn senior

Leak trong production thường tinh tế — không phải trong closure rõ ràng mà trong observer chain, analytics hook, hoặc background task sống lâu hơn màn hình. Dùng Memory Graph trong QA, không chỉ trong development.

## Bài tập

Thêm `deinit { print("deinit \(Self.self)") }` vào ViewController dùng `Timer` và `NotificationCenter` observer. Navigate đi và xác nhận deinit được gọi. Nếu không, dùng Memory Graph Debugger để tìm retain cycle và sửa.
