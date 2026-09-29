[English](./Actors.md) | [Tiếng Việt](./Actors.vi.md)

[← Concurrency](./README.vi.md)

# Actor và MainActor

## Ý chính

`Actor` tuần tự hóa việc truy cập vào mutable state, ngăn data race mà không cần lock thủ công. `@MainActor` đảm bảo code chạy trên main thread.

## Nội dung ôn tập

- `actor` — reference type mà mutable state bên trong được isolate: code bên ngoài chỉ truy cập được qua `await`, và actor chạy tối đa một đoạn code của nó tại một thời điểm, nên không có data race.
- `@MainActor` — global actor gắn với main thread; đánh dấu lên class, function hoặc property để compiler buộc mọi truy cập từ nơi khác phải hop sang main thread.
- Actor reentrancy — khi một method của actor gặp `await` và bị suspend, actor được nhả ra để chạy các lời gọi khác; lúc method resume, state có thể đã bị thay đổi.
- `nonisolated` — opt out khỏi actor isolation cho member cụ thể (ví dụ một computed property chỉ đọc dữ liệu `let` bất biến), để gọi được mà không cần `await`; member đó không được đụng vào mutable state của actor.

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

## Đáp án câu hỏi luyện tập

### Bug vẫn có thể xảy ra khi nào dù bạn đã dùng Actor?

Actor chỉ ngăn data race ở mức bộ nhớ (hai thread cùng ghi một biến); nó không ngăn race ở mức logic, và nguồn bug lớn nhất là reentrancy tại mỗi `await`.

Cơ chế: actor chỉ chạy một đoạn code tại một thời điểm, nhưng khi method của actor gặp `await`, nó nhả actor ra và các lời gọi khác được chạy xen vào. Khi quay lại, state có thể đã khác. Ví dụ mở rộng `ImageCache` thêm một method tải ảnh:

```swift
func load(_ url: URL) async throws -> UIImage {
    if let cached = cache[url] { return cached }
    let image = try await download(url)   // actor bị nhả ở đây
    cache[url] = image                    // caller khác có thể đã ghi trước
    return image
}
```

Hai caller cùng gọi `load` cho một URL sẽ tải hai lần. Cách sửa là lưu `Task` đang chạy vào dictionary để caller sau `await` cùng một task, và luôn kiểm tra lại state sau mỗi `await`:

```swift
private var inFlight: [URL: Task<UIImage, Error>] = [:]

func load(_ url: URL) async throws -> UIImage {
    if let cached = cache[url] { return cached }
    if let task = inFlight[url] { return try await task.value }   // dùng chung lần tải đang chạy
    let task = Task { try await download(url) }
    inFlight[url] = task          // ghi trước khi await: không có khe hở nào
    defer { inFlight[url] = nil }
    let image = try await task.value
    cache[url] = image
    return image
}
```

Các trường hợp khác:
- Check-then-act từ bên ngoài: `if await cache.image(for: url) == nil { await cache.store(...) }` là hai lần gọi riêng, ở giữa có thể có caller khác.
- Trả ra một reference type không `Sendable` từ actor, rồi code bên ngoài sửa nó mà không có bảo vệ. Ở Swift 6 language mode compiler thường chặn việc này; nhưng ở Swift 5 mode, hoặc khi type bị đánh dấu `@unchecked Sendable` / import qua `@preconcurrency`, lỗi vẫn lọt qua.
- Giả định thứ tự: các lời gọi từ những task khác nhau không đảm bảo chạy theo thứ tự bạn gọi.

Trade-off: gom logic cần tính nguyên tử vào một method đồng bộ (không có `await`) bên trong actor là cách đơn giản nhất.

## Bẫy phỏng vấn

### "Actor có chạy trên một thread riêng của nó không?"

**Dễ trả lời sai:** "Có, mỗi actor giống như một serial `DispatchQueue` có thread riêng." Hình dung này dẫn đến giả định sai về thread-local và hiệu năng.

**Nên trả lời:** Actor thường không gắn với thread nào; code của nó chạy trên cooperative thread pool dùng chung, và có thể ở thread khác nhau giữa các lần `await`. Actor chỉ đảm bảo tại một thời điểm có tối đa một đoạn code của nó đang chạy. Ngoại lệ là `MainActor`, vốn gắn với main thread. Vì vậy đừng dùng thread-local storage hay kiểm tra `Thread.current` để suy luận về actor.

### "Actor có bị deadlock khi method của nó gọi `await` vào chính nó hoặc actor khác không?"

**Dễ trả lời sai:** "Có, giống như lock gọi lồng nhau, A chờ B và B chờ A sẽ deadlock." Đây là suy nghĩ mang từ lock/serial queue sang.

**Nên trả lời:** Actor trong Swift là reentrant nên không deadlock kiểu đó: khi đang `await`, actor được nhả ra để xử lý lời gọi khác. Cái giá phải trả chính là reentrancy bug ở câu trên. Swift chọn đánh đổi này có chủ đích: tránh deadlock nhưng buộc developer không được giả định state ổn định qua `await`.

### "Đánh dấu class là `@MainActor` thì mọi method chắc chắn chạy trên main thread?"

**Dễ trả lời sai:** "Chắc chắn, kể cả khi SDK cũ gọi delegate method từ background queue." Thật ra ban đầu đây là đảm bảo lúc compile, không phải phép màu lúc runtime.

**Nên trả lời:** Compiler đảm bảo mọi lời gọi từ code Swift đã được kiểm tra concurrency phải hop sang main actor. Nhưng code Objective-C hoặc code không được kiểm tra (callback của GCD, delegate của framework cũ) có thể gọi thẳng vào method đó từ background thread. Swift 5 mode sẽ âm thầm chạy sai thread; Swift 6 language mode (SE-0423) thêm dynamic isolation check ở các ranh giới với code chưa được kiểm tra, như `@preconcurrency` conformance hay thunk `@objc`, và sẽ crash để lộ bug. Ngoài ra, method `nonisolated` hoặc closure `@Sendable` bên trong class vẫn không chạy trên main actor.

## Bài tập

Implement `actor RequestCounter` với `func increment()`, `func decrement()`, và `private(set) var count: Int`. Tạo 100 task chạy đồng thời (ví dụ bằng `withTaskGroup`), mỗi task gọi `await counter.increment()` rồi `await counter.decrement()`. Chờ tất cả xong rồi assert count cuối cùng là 0 (đúng, vì mỗi method đồng bộ bên trong actor là nguyên tử).

Sau đó cố ý tạo lỗi reentrancy **bên trong actor**: viết thêm `func slowIncrement() async` đọc `let current = count`, rồi `await Task.yield()` (hoặc `try? await Task.sleep(for: .milliseconds(1))`), rồi gán `count = current + 1`. Gọi nó 100 lần đồng thời và quan sát count cuối nhỏ hơn 100. Giải thích trong comment: tại điểm `await` actor được nhả ra, các lời gọi khác cũng đọc cùng giá trị cũ, nên các lần ghi đè lên nhau (lost update). Lưu ý: chỉ chèn `await` giữa hai lời gọi `increment()`/`decrement()` từ bên ngoài thì không làm sai count, vì mỗi method vẫn chạy trọn vẹn.
