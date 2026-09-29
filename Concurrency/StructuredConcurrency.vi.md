[English](./StructuredConcurrency.md) | [Tiếng Việt](./StructuredConcurrency.vi.md)

[← Concurrency](./README.vi.md)

# Structured Concurrency

## Ý chính

Structured concurrency gắn lifetime của child task vào parent scope: scope chỉ được thoát khi mọi child task đã kết thúc, nên không child nào sống lâu hơn nơi tạo ra nó. Khi parent bị cancel, cancellation tự lan xuống mọi child; khi scope thoát do lỗi (hoặc còn `async let` chưa được `await`), các child còn chạy bị cancel rồi được chờ cho xong trước khi thoát.

## Nội dung ôn tập

- `async let` — tạo một child task chạy ngay tại dòng khai báo, song song với code phía sau; bạn `await` biến đó khi cần kết quả. Phù hợp khi số việc cố định.
- `withTaskGroup` / `withThrowingTaskGroup` — dynamic fan-out: thêm bao nhiêu child tùy ý bằng `group.addTask` (ví dụ trong vòng lặp), rồi đọc kết quả theo thứ tự hoàn thành.
- Task hierarchy — child task thuộc về parent: cancel parent thì mọi child bị cancel, và parent không thể kết thúc trước child.
- Task priority propagation — child task kế thừa priority của parent; nếu một task priority cao đang chờ kết quả của task priority thấp hơn, runtime có thể nâng priority (priority escalation) để tránh priority inversion.

## Ví dụ

```swift
func loadDashboard() async throws -> Dashboard {
    async let user = fetchUser()
    async let feed = fetchFeed()
    return try await Dashboard(user: user, feed: feed)
}
```

```swift
func fetchAll(ids: [String]) async throws -> [Item] {
    try await withThrowingTaskGroup(of: Item.self) { group in
        for id in ids {
            group.addTask { try await fetchItem(id: id) }
        }
        return try await group.reduce(into: []) { $0.append($1) }
    }
}
```

## Câu hỏi luyện tập

- Khi nào async let rõ ràng hơn cho một function loadProfile() fetch đồng thời user, posts và followers, và khi nào withThrowingTaskGroup trở nên cần thiết thay thế?

## Góc nhìn Senior

Structured concurrency không chỉ là tiện ích cú pháp. Nó cung cấp mô hình ownership rõ ràng: task được giới hạn scope, leak khó xảy ra hơn, và cancellation tự động lan truyền. Ưu tiên dùng structured concurrency thay vì `Task { }` không có cấu trúc khi lifetime được giới hạn.

## Đáp án câu hỏi luyện tập

### Khi nào async let rõ ràng hơn cho một function loadProfile() fetch đồng thời user, posts và followers, và khi nào withThrowingTaskGroup trở nên cần thiết thay thế?

`async let` rõ ràng hơn khi số lượng việc cố định và biết trước lúc viết code, mỗi việc trả về một kiểu khác nhau; `withThrowingTaskGroup` cần thiết khi số lượng việc chỉ biết lúc runtime, hoặc cần xử lý kết quả theo thứ tự hoàn thành.

Với `loadProfile()`, ba request `user`, `posts`, `followers` là cố định và khác kiểu (`User`, `[Post]`, `[User]`), nên `async let` đọc gần như code tuần tự và giữ được type của từng biến:

```swift
func loadProfile() async throws -> Profile {
    async let user = fetchUser()
    async let posts = fetchPosts()
    async let followers = fetchFollowers()
    return try await Profile(user: user, posts: posts, followers: followers)
}
```

Task group bắt buộc mọi child trả về cùng một kiểu (`of: Item.self`), nên dùng group cho ba kiểu khác nhau phải bọc vào một enum rồi switch lại, dài và dễ sai. Nhưng group thắng khi:
- Danh sách request là một mảng động (ví dụ `fetchAll(ids:)` trong phần ví dụ, hay bật/tắt section theo feature flag).
- Muốn giới hạn số request đồng thời (chỉ thêm task mới khi một task cũ xong).
- Muốn hiển thị dần từng kết quả, hoặc dừng sớm khi có kết quả đầu tiên.

Cả hai đều là structured: function chỉ return sau khi mọi child đã kết thúc, và khi lỗi của một child được lan ra khỏi scope thì các child còn lại bị cancel. Lưu ý lỗi chỉ lan ra khi bạn `await` đúng child đó (với `async let`) hoặc đọc kết quả từ group (xem bẫy bên dưới). Với `async let`, các biến được `await` theo thứ tự viết trong biểu thức, nên nếu `posts` lỗi sớm nhưng `user` chậm, lỗi chỉ được throw sau khi `user` xong.

## Bẫy phỏng vấn

### "`async let` bắt đầu chạy khi nào? Nếu không `await` nó thì sao?"

**Dễ trả lời sai:** "Nó chạy khi mình `await`, và nếu không `await` thì nó tiếp tục chạy ngầm như `Task { }`." Cả hai vế đều sai.

**Nên trả lời:** Child task của `async let` bắt đầu ngay tại dòng khai báo; `await` chỉ là chỗ lấy kết quả. Nếu scope kết thúc mà chưa `await`, Swift tự cancel child đó rồi vẫn chờ nó kết thúc trước khi thoát scope, nên không có task nào "rò rỉ" ra ngoài. Hệ quả: một `async let` bị quên không làm request chạy ngầm, nhưng function vẫn có thể phải chờ nó dừng.

### "Trong `withThrowingTaskGroup`, một child throw thì các child khác bị cancel ngay đúng không?"

**Dễ trả lời sai:** "Đúng, lỗi đầu tiên luôn làm cả group dừng." Điều này chỉ đúng khi bạn thật sự đọc kết quả từ group.

**Nên trả lời:** Lỗi của child chỉ được rethrow khi bạn lấy kết quả qua `next()`, `for try await` hoặc `reduce` như trong `fetchAll`. Khi lỗi thoát khỏi body của group, các child còn lại mới bị cancel. Nếu body không bao giờ đọc kết quả, group ngầm chờ mọi child chạy xong và lỗi của chúng bị bỏ qua. Nếu chỉ cần chạy việc mà không cần kết quả, `withThrowingDiscardingTaskGroup` (iOS 17+) cancel cả group ngay khi một child throw.

### "`fetchAll(ids:)` trả về item theo đúng thứ tự `ids` không?"

**Dễ trả lời sai:** "Có, vì task được thêm vào theo thứ tự trong vòng lặp." Thứ tự thêm task không phải thứ tự nhận kết quả.

**Nên trả lời:** Group trả kết quả theo thứ tự child hoàn thành, nên `reduce(into: [])` tạo mảng theo thứ tự request nào về trước. Nếu UI cần giữ thứ tự, trả kèm index hoặc id từ child rồi sắp xếp lại, hoặc gom vào dictionary.

```swift
try await withThrowingTaskGroup(of: (Int, Item).self) { group in
    for (index, id) in ids.enumerated() {
        group.addTask { (index, try await fetchItem(id: id)) }
    }
    var result = [(Int, Item)]()
    for try await pair in group { result.append(pair) }
    return result.sorted { $0.0 < $1.0 }.map { $0.1 }
}
```

## Bài tập

Viết function `loadProfile() async throws -> Profile` fetch `user`, `posts`, và `followers` đồng thời dùng `async let`. Sau đó viết lại function tương tự dùng `withThrowingTaskGroup` để tập hợp requests có thể được điều khiển bởi dynamic array. Viết comment so sánh hai cách: khi nào `async let` rõ ràng hơn, khi nào `TaskGroup` trở nên cần thiết?
