[English](./URLSession.md) | [Tiếng Việt](./URLSession.vi.md)

[← Networking](./README.vi.md)

# URLSession

## Ý chính

`URLSession` là HTTP client tiêu chuẩn trên iOS. Với hầu hết app, `URLSession.shared` là đủ. Dùng custom configuration cho timeout, caching và background transfer.

## Nội dung ôn tập

- `URLSession.shared` vs custom `URLSession(configuration:)`
- `data(from:)` — async/await API (iOS 15+)
- `URLSessionConfiguration` — timeout, cache policy, waitsForConnectivity
- Background sessions — `URLSessionConfiguration.background(withIdentifier:)`
- `URLRequest` — method, headers, body, timeout

## Ví dụ

```swift
struct APIClient {
    private let session: URLSession

    init(session: URLSession = .shared) {
        self.session = session
    }

    func fetch<T: Decodable>(_ type: T.Type, from url: URL) async throws -> T {
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        return try JSONDecoder().decode(type, from: data)
    }
}
```

## Câu hỏi luyện tập

- Tại sao việc inject URLSession qua init lại giúp bạn test được fetch(_:from:) của một APIClient generic bằng URLProtocol stub cho cả trường hợp decode JSON hợp lệ lẫn trường hợp status non-200 ném ra APIError.invalidResponse?

## Góc nhìn Senior

Inject `URLSession` như một dependency — giúp client testable mà không cần hit real network. Dùng `URLProtocol` subclass để intercept request trong test.

## Bài tập

Xây dựng generic `APIClient` với `func fetch<T: Decodable>(_ type: T.Type, from url: URL) async throws -> T`. Inject `URLSession` qua `init`. Viết hai test dùng `URLProtocol` stub: một trả về JSON hợp lệ và assert decode đúng, một trả về status non-200 và assert `APIError.invalidResponse` được throw.
