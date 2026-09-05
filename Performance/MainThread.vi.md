[English](./MainThread.md) | [Tiếng Việt](./MainThread.vi.md)

[← Performance](./README.vi.md)

# Main Thread Discipline

## Ý tưởng chính

Main thread chịu trách nhiệm cho tất cả cập nhật UI. Blocking nó gây dropped frame (jank). Mọi công việc không liên quan đến UI phải được thực hiện trên background thread.

## Các vi phạm phổ biến

- Decode JSON trên main thread sau khi nhận network response
- Fetch từ Core Data đồng bộ trên main thread
- Giải nén ảnh trên main thread
- Tính toán nặng trong `body` hoặc `cellForItemAt`

## Phát hiện

- Xcode: Main Thread Checker (bật mặc định trong debug)
- Instruments: Time Profiler — tìm các frame main-thread dài
- `Thread.isMainThread` assertions ở các đường dẫn quan trọng

## Ví dụ sửa lỗi

```swift
// Sai: decode trên main thread
func didReceiveData(_ data: Data) {
    let items = try? JSONDecoder().decode([Item].self, from: data) // blocks main
    self.items = items
}

// Đúng: decode ngoài main, cập nhật trên main
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

`@MainActor` trên ViewModel không có nghĩa là tất cả công việc chạy trên main thread — nó có nghĩa là các property và method được truy cập trên main thread. Async work bên trong hàm `@MainActor` suspend sang background thread khi await, đây là hành vi đúng.

## Bài tập

Bạn có `SearchViewModel` decode JSON response lớn và filter kết quả trên main thread trong `didReceiveData`. Refactor để decode và filter trên background thread dùng `Task.detached`, sau đó publish kết quả về trên `@MainActor`. Xác minh tính đúng đắn với Main Thread Checker.
