[English](./URLSession.md) | [Tiếng Việt](./URLSession.vi.md)

[← Networking](./README.md)

# URLSession

## Key Idea

`URLSession` is the standard HTTP client in iOS. For most apps, `URLSession.shared` is sufficient. Use custom configurations for timeout, caching, and background transfers.

## What To Review

- `URLSession.shared` vs custom `URLSession(configuration:)` — `shared` is a singleton with the default configuration; you cannot change its configuration or attach a delegate. When you need custom timeouts, caching, shared headers or your own delegate, create a session with `URLSession(configuration:delegate:delegateQueue:)`.
- `data(from:)` / `data(for:)` — async/await APIs (iOS 15+) that return `(Data, URLResponse)`; `data(for:)` takes a `URLRequest` when you need to set the method, headers or body.
- `URLSessionConfiguration` — `.default` (on-disk cache and cookies), `.ephemeral` (memory only, nothing written to disk), `.background(withIdentifier:)`; commonly used properties: `timeoutIntervalForRequest`, `requestCachePolicy`, `urlCache`, `waitsForConnectivity` (wait for a network instead of failing immediately).
- Background sessions — `URLSessionConfiguration.background(withIdentifier:)`: the system performs downloads/uploads in a separate process and keeps going while the app is suspended; you must use a delegate (see the trap below).
- `URLRequest` — method, headers, body and timeout per request; a header set on the request takes precedence over the shared headers in the configuration's `httpAdditionalHeaders`.

## Example

```swift
enum APIError: Error {
    case invalidResponse
}

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

## Practice Question Answers

### Why does making URLSession injectable via init let you test a generic APIClient's fetch(_:from:) with a URLProtocol stub for both valid JSON decoding and a non-200 APIError.invalidResponse case?

Because when `URLSession` is passed in through `init`, a test can hand in its own session whose `protocolClasses` contains a `URLProtocol` stub, so every request made by `fetch(_:from:)` is intercepted inside the process and never reaches the real network.

How it works: the URL Loading System asks each `URLProtocol` in the configuration, in order, whether it wants to handle the request (`canInit(with:)`). The stub accepts everything and builds an `HTTPURLResponse` with whatever status code and `Data` the test wants. The production code in `APIClient` does not change at all — it still calls `session.data(from:)`, still checks `statusCode == 200`, still decodes. So one test returns valid JSON with a 200 to check decoding, and the other returns a 500 to assert that `APIError.invalidResponse` is thrown.

```swift
let config = URLSessionConfiguration.ephemeral
config.protocolClasses = [StubURLProtocol.self]
let client = APIClient(session: URLSession(configuration: config))
```

If `APIClient` hard-coded `URLSession.shared`, your only option would be a global `URLProtocol.registerClass` — which affects every other test running at the same time.

Trade-off: `StubURLProtocol` usually keeps its handler in a `static` variable, so with Swift Testing (parallel by default) you need to mark the suite `.serialized` or key handlers by URL. If you only want to test mapping logic and do not care about HTTP, a small mockable `HTTPClient` protocol can be simpler.

## Interview Traps

### Does `data(from:)` throw when the server returns a 404 or a 500?

**Common wrong answer:** "Yes, a failed request makes `try await` throw." Many people assume an HTTP error status is treated as an error just like `URLError`.

**Better answer:** No. `URLSession` only throws for transport-level failures (no network, timeout, cancellation, TLS errors…) as `URLError`. A 404 or 500 is still a valid HTTP response, so you get `(data, response)` back normally and must check `statusCode` yourself — that is why `APIClient` has `guard http.statusCode == 200`. In practice you should accept the whole `200..<300` range rather than exactly 200.

### Is it fine to create a new `URLSession(configuration:delegate:delegateQueue:)` for every request?

**Common wrong answer:** "Sure, sessions are lightweight; ARC frees them when you are done."

**Better answer:** A session holds a strong reference to its delegate until it is invalidated, so unless you call `finishTasksAndInvalidate()` or `invalidateAndCancel()`, both the session and the delegate leak. Each session also has its own connection pool, cache and cookies, so creating new ones constantly loses connection reuse (HTTP/2, TLS resumption) and is slower. Create a few long-lived sessions split by configuration needs, and inject them.

### Can a background session use `try await session.data(from:)` like a normal session?

**Common wrong answer:** "Yes, just switch the configuration to `.background(withIdentifier:)` and the request keeps running while the app is suspended."

**Better answer:** Background sessions are built around a delegate: completion-handler APIs are rejected at runtime, and the async convenience methods are not the right fit either, because the transfer has to continue when your app's process is no longer running. The system performs download tasks and upload tasks (from a file) in a separate process, and may relaunch your app to call `application(_:handleEventsForBackgroundURLSession:completionHandler:)` (or `.backgroundTask(.urlSession)` in SwiftUI). Use a default session for normal API requests; a background session is only for large transfers that must survive the app being suspended or terminated by the system.

## Exercise

Build a generic `APIClient` with `func fetch<T: Decodable>(_ type: T.Type, from url: URL) async throws -> T`. Make `URLSession` injectable via `init`. Write two tests using a `URLProtocol` stub: one that returns valid JSON and asserts correct decoding, one that returns a non-200 status and asserts `APIError.invalidResponse` is thrown.
