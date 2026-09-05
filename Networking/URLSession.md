[English](./URLSession.md) | [Tiếng Việt](./URLSession.vi.md)

[← Networking](./README.md)

# URLSession

## Key Idea

`URLSession` is the standard HTTP client in iOS. For most apps, `URLSession.shared` is sufficient. Use custom configurations for timeout, caching, and background transfers.

## What To Review

- `URLSession.shared` vs custom `URLSession(configuration:)`
- `data(from:)` — async/await API (iOS 15+)
- `URLSessionConfiguration` — timeout, cache policy, waitsForConnectivity
- Background sessions — `URLSessionConfiguration.background(withIdentifier:)`
- `URLRequest` — method, headers, body, timeout

## Example

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

## Practice Questions

- Why does making URLSession injectable via init let you test a generic APIClient's fetch(_:from:) with a URLProtocol stub for both valid JSON decoding and a non-200 APIError.invalidResponse case?

## Senior Take

Inject `URLSession` as a dependency — it makes the client testable without hitting real network. Use `URLProtocol` subclasses to intercept requests in tests.

## Exercise

Build a generic `APIClient` with `func fetch<T: Decodable>(_ type: T.Type, from url: URL) async throws -> T`. Make `URLSession` injectable via `init`. Write two tests using a `URLProtocol` stub: one that returns valid JSON and asserts correct decoding, one that returns a non-200 status and asserts `APIError.invalidResponse` is thrown.
