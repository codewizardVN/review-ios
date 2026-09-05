[English](./Actors.md) | [Tiếng Việt](./Actors.vi.md)

[← Concurrency](./README.vi.md)

# Actor và MainActor

## Ý chính

`Actor` tuần tự hóa việc truy cập vào mutable state, ngăn data race mà không cần lock thủ công. `@MainActor` đảm bảo code chạy trên main thread.

## Nội dung ôn tập

- `actor` — reference type với isolated mutable state
- `@MainActor` — annotation để gắn class, function hoặc property vào main thread
- Actor reentrancy — một `await` bị suspend bên trong actor có thể cho phép công việc khác chạy
- `nonisolated` — opt out khỏi actor isolation cho các member cụ thể

## Ví dụ

```swift
actor ImageCache {
    private var cache: [URL: UIImage] = [:]

    func image(for url: URL) -> UIImage? {
        cache[url]
    }

    func store(_ image: UIImage, for url: URL) {
        cache[url] = image
    }
}

@MainActor
final class FeedViewModel: ObservableObject {
    @Published var items: [FeedItem] = []
}
```

## Câu hỏi thực hành

- Bug có thể vẫn xảy ra dù dùng `Actor` trong trường hợp nào?

## Câu hỏi luyện tập

- Bug vẫn có thể xảy ra khi nào dù bạn đã dùng Actor?

## Góc nhìn Senior

Actor reentrancy là bất ngờ phổ biến nhất. State có thể thay đổi giữa hai điểm `await` trong cùng một actor method, vì vậy đừng giả định state là ổn định qua các lần suspension.

## Bài tập

Implement `actor RequestCounter` với `func increment()`, `func decrement()`, và `var count: Int`. Tạo 100 `Task { }` đồng thời, mỗi task gọi `increment()` rồi `decrement()`. Assert count cuối cùng là 0. Sau đó cố ý tạo lỗi reentrancy bằng cách chèn `await` giữa increment và decrement. Giải thích trong comment state corruption nào có thể xảy ra và tại sao.
