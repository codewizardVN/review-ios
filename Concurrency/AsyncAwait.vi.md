[English](./AsyncAwait.md) | [Tiếng Việt](./AsyncAwait.vi.md)

[← Concurrency](./README.vi.md)

# async/await

## Ý chính

`async/await` giúp code bất đồng bộ đọc như code đồng bộ, loại bỏ callback lồng nhau và giúp luồng điều khiển dễ hiểu hơn.

## Nội dung ôn tập

- Đánh dấu function với `async`
- Gọi async function bằng `await`
- Truyền lỗi với `async throws`
- Bridging từ completion handler dùng `withCheckedContinuation` / `withCheckedThrowingContinuation`

## Ví dụ

```swift
func fetchUser(id: String) async throws -> User {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}
```

## Góc nhìn Senior

Tại sao `async/await` dễ bảo trì hơn callback chain: luồng điều khiển là tuyến tính, xử lý lỗi thống nhất qua `throws`, và compiler kiểm tra tính đúng đắn trong quá trình biên dịch.

## Bài tập

Viết lại function dùng completion handler sau bằng async/await:

```swift
func fetchUser(id: String, completion: @escaping (Result<User, Error>) -> Void)
```

Sau đó wrap phiên bản async mới trở lại thành completion-handler API dùng `withCheckedThrowingContinuation`. Viết comment giải thích tình huống thực tế nào vẫn cần wrapper (gợi ý: caller dùng delegate-based hoặc callback-based).
