[English](./Tasks.md) | [Tiếng Việt](./Tasks.vi.md)

[← Concurrency](./README.vi.md)

# Task và Cancellation

## Ý chính

`Task` là đơn vị công việc bất đồng bộ trong Swift Concurrency. Hiểu rõ ownership và cancellation là điều kiện cần để viết code production an toàn.

## Nội dung ôn tập

- `Task { }` — kế thừa actor context và priority từ calling context
- `Task.detached { }` — không kế thừa context; hoàn toàn độc lập
- `Task.cancel()` — cooperative cancellation qua `Task.isCancelled`
- `withTaskCancellationHandler` — phản ứng ngay khi cancellation xảy ra
- `TaskGroup` — fan-out công việc song song với structured lifecycle

## Ví dụ

```swift
final class FeedViewModel: ObservableObject {
    private var loadTask: Task<Void, Never>?

    func load() {
        loadTask?.cancel()
        loadTask = Task {
            await fetchFeed()
        }
    }
}
```

## Câu hỏi thực hành

- Nếu người dùng rời khỏi màn hình, request đang thực thi nên được xử lý như thế nào?
- Sự khác biệt giữa `Task.detached` và `Task` thông thường là gì?

## Góc nhìn Senior

Cancellation trong Swift là cooperative — bạn phải tự kiểm tra `Task.isCancelled` hoặc dùng `try Task.checkCancellation()` bên trong task body. Cancel một task không tự động dừng nó.

## Bài tập

Xây dựng `SearchViewModel` với method `func search(query: String) async` tự cancel task search trước khi bắt đầu search mới. Dùng `task?.cancel()` và bắt `CancellationError` trong `catch` block in ra "cancelled". Gọi `search(query:)` ba lần liên tiếp nhanh và xác nhận chỉ kết quả cuối cùng được áp dụng. Giải thích tại sao pattern này quan trọng với search field.
