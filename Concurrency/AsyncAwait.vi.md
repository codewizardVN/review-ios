[English](./AsyncAwait.md) | [Tiếng Việt](./AsyncAwait.vi.md)

[← Concurrency](./README.vi.md)

# async/await

## Ý chính

`async/await` giúp code bất đồng bộ đọc như code đồng bộ, loại bỏ callback lồng nhau và giúp luồng điều khiển dễ hiểu hơn.

## Nội dung ôn tập

- Đánh dấu function với `async`: function đó có thể tạm dừng (suspend) giữa chừng để chờ việc khác xong, rồi chạy tiếp.
- Gọi async function bằng `await`: mỗi `await` là một điểm suspension tiềm năng; chỉ gọi được từ một ngữ cảnh async (function `async` khác hoặc bên trong `Task`).
- Truyền lỗi với `async throws`: caller viết `try await`, lỗi được bắt bằng `do/catch` như code đồng bộ, không cần truyền `Error?` qua callback.
- Bridging từ completion handler **sang** async dùng `withCheckedContinuation` / `withCheckedThrowingContinuation`: bọc một API callback cũ để gọi được bằng `await`. Chiều ngược lại (cho caller cũ gọi code async) thì dùng `Task { }` bên trong function có completion.

## Ví dụ

```swift
func fetchUser(id: String) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}
```

## Câu hỏi luyện tập

- Sau khi viết lại function fetchUser dùng completion handler bằng async/await, trong tình huống thực tế nào bạn vẫn cần giữ một bản completion-handler, và bạn bọc nó bằng gì (vì sao không dùng withCheckedThrowingContinuation cho chiều này)?

## Góc nhìn Senior

Tại sao `async/await` dễ bảo trì hơn callback chain: luồng điều khiển là tuyến tính, xử lý lỗi thống nhất qua `throws`, và compiler kiểm tra tính đúng đắn trong quá trình biên dịch.

## Đáp án câu hỏi luyện tập

### Sau khi viết lại function fetchUser dùng completion handler bằng async/await, trong tình huống thực tế nào bạn vẫn cần giữ một bản completion-handler, và bạn bọc nó bằng gì (vì sao không dùng withCheckedThrowingContinuation cho chiều này)?

Bạn vẫn cần một API dạng completion handler khi caller chưa thể dùng `async`: code Objective-C, code dựa trên delegate hoặc callback cũ, hoặc một SDK public phải giữ nguyên chữ ký cho client đang dùng. Codebase lớn thường migrate dần, nên trong một thời gian cả hai dạng API phải cùng tồn tại.

Cần nói rõ một điểm mà interviewer hay kiểm tra: `withCheckedThrowingContinuation` đi theo chiều ngược lại. Nó bọc một API callback **thành** `async` (ví dụ bọc một hàm Swift cũ `fetchToken(completion:)`, hay một API dựa trên delegate, để gọi bằng `await`; riêng method Objective-C có completion handler đúng quy ước như `LegacySessionManager.fetchToken` thì compiler đã tự sinh sẵn bản `async`), nên không thể dùng nó để biến một function `async` thành completion handler. Còn muốn expose bản `async` mới cho caller callback, bạn tạo một `Task` bên trong function có completion:

```swift
// Chiều async -> callback: dùng Task. Ở Swift 6 closure cần @Sendable
// (và User cần Sendable) vì nó được mang sang một Task khác.
func fetchUser(id: String, completion: @escaping @Sendable (Result<User, Error>) -> Void) {
    Task {
        do { completion(.success(try await fetchUser(id: id))) }
        catch { completion(.failure(error)) }
    }
}
```

Hai chiều thường xuất hiện cùng nhau: tầng thấp là callback cũ được bọc bằng continuation, tầng giữa viết bằng `async`, tầng trên còn callback thì bọc lại bằng `Task`. Với method `@objc` trong class, compiler tự sinh bản completion handler cho Objective-C nên nhiều khi không cần tự viết wrapper.

Trade-off: wrapper dùng `Task` là unstructured, caller không cancel được trừ khi bạn trả `Task` về hoặc tự quản lý nó; và bạn phải tự quyết định completion được gọi trên thread nào. Nên xóa wrapper khi caller cuối cùng đã chuyển sang `async`.

## Bẫy phỏng vấn

### "`await` có block thread hiện tại không?"

**Dễ trả lời sai:** "Có, `await` chờ giống như `DispatchSemaphore.wait()`, nên đừng gọi trên main thread." Câu này nhầm giữa suspend và block.

**Nên trả lời:** `await` là một điểm suspension: task hiện tại tạm dừng và nhả thread lại cho executor chạy việc khác, nên main thread vẫn xử lý UI trong lúc `URLSession` đang chờ mạng. Khi kết quả về, task được resume, có thể trên một thread khác (trừ khi nó bị isolate vào `@MainActor`). Cái thật sự block thread là code đồng bộ nặng giữa hai lần `await`, hoặc dùng semaphore để chờ một task async, việc này có thể gây deadlock cho cooperative thread pool.

### "Nếu continuation không bao giờ được resume, hoặc bị resume hai lần thì sao?"

**Dễ trả lời sai:** "Không sao, callback gọi hai lần thì chỉ lấy lần đầu, không gọi thì coi như timeout." Swift không có cơ chế tự bỏ qua hay timeout nào như vậy.

**Nên trả lời:** Continuation phải được resume đúng một lần. Với `withCheckedThrowingContinuation`, resume lần hai sẽ crash lúc runtime; không resume thì task bị treo mãi và runtime in cảnh báo "SWIFT TASK CONTINUATION MISUSE" khi continuation bị giải phóng. Bản `withUnsafe...` bỏ các kiểm tra này, lỗi sẽ âm thầm hơn. Vì vậy mọi nhánh của callback cũ (kể cả nhánh `guard ... else { return }`) đều phải gọi `resume`.

### "Function `async` có tự chạy ở background thread không?"

**Dễ trả lời sai:** "Có, đánh dấu `async` là code chạy khỏi main thread, nên có thể decode JSON nặng thoải mái." `async` chỉ nói function có thể suspend, không nói nó chạy ở đâu.

**Nên trả lời:** Nơi chạy do isolation quyết định. Function được isolate vào `@MainActor` (tự đánh dấu, hoặc là method của một type `@MainActor`) chạy phần đồng bộ trên main thread, nên `JSONDecoder().decode` nặng ở đó vẫn làm giật UI. Hành vi của function `nonisolated async` còn phụ thuộc phiên bản và cài đặt: từ Swift 5.7 (SE-0338) nó luôn chuyển sang global executor (tức là rời main thread). Từ Swift 6.2 (SE-0461), nếu bật upcoming feature `NonisolatedNonsendingByDefault` (nằm trong nhóm cài đặt "Approachable Concurrency" của Xcode 26) thì mặc định nó chạy trên actor của caller; khi đó bạn đánh dấu `@concurrent` khi thật sự muốn đẩy ra background. Nếu không bật feature này, Swift 6.2 vẫn giữ hành vi cũ.

## Bài tập

Viết lại function dùng completion handler sau bằng async/await:

```swift
func fetchUser(id: String, completion: @escaping (Result<User, Error>) -> Void)
```

Sau đó làm hai việc bridging theo đúng chiều:

1. Giả sử tầng dưới là một API callback cũ viết bằng Swift, ví dụ `func fetchToken(completion: @escaping (String?, Error?) -> Void)`. Dùng `withCheckedThrowingContinuation` để bọc nó thành `func fetchToken() async throws -> String`, và bảo đảm mọi nhánh đều gọi `resume` đúng một lần.
2. Cung cấp lại một bản completion-handler của `fetchUser` cho caller cũ bằng cách gọi bản async bên trong `Task { }`. Viết comment giải thích tình huống thực tế nào vẫn cần wrapper này (gợi ý: caller dùng delegate-based hoặc callback-based, code Objective-C, SDK public phải giữ chữ ký).
