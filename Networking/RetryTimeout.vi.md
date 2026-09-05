[English](./RetryTimeout.md) | [Tiếng Việt](./RetryTimeout.vi.md)

[← Networking](./README.vi.md)

# Retry, Timeout và Cancellation

## Timeout

Set ở `URLRequest` hoặc `URLSessionConfiguration`:

```swift
var request = URLRequest(url: url)
request.timeoutInterval = 10
```

## Retry

Retry hợp lý cho transient error (mất mạng thoáng qua, 503). Không retry:
- 4xx client error (request sai sẽ không thành công dù retry)
- Mutation không idempotent

```swift
func fetchWithRetry(url: URL, attempts: Int = 3) async throws -> Data {
    for attempt in 1...attempts {
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            return data
        } catch {
            if attempt == attempts { throw error }
            try await Task.sleep(for: .seconds(Double(attempt)))
        }
    }
    fatalError("unreachable")
}
```

## Cancellation

Cancel qua `Task.cancel()`. `URLSession` task đang chạy tự động bị cancel khi Swift Concurrency task bị cancel.

## Câu hỏi thực hành

- Khi nào retry hợp lý và khi nào không?
- Làm sao tránh duplicate request khi người dùng thao tác nhanh?

## Câu hỏi luyện tập

- Khi nào retry hợp lý và khi nào không?
- Làm sao bạn tránh duplicate request khi user thao tác nhanh?

## Góc nhìn Senior

Exponential backoff với jitter tốt hơn fixed-interval retry trong production — tránh thundering herd khi nhiều client thất bại cùng lúc.

## Bài tập

Viết `fetchWithRetry(url:maxAttempts:) async throws -> Data` với exponential backoff (1s, 2s, 4s). Chỉ retry với `URLError`, không retry với 4xx HTTP. Viết hai test: một nơi lần thử thứ 2 thành công và assert data được trả về, một nơi tất cả lần thử thất bại và assert original error được rethrow. Giải thích trong comment tại sao POST request thường KHÔNG nên được retry.
