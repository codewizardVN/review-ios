[English](./RetryTimeout.md) | [Tiếng Việt](./RetryTimeout.vi.md)

[← Networking](./README.md)

# Retry, Timeout, and Cancellation

## Timeout

Set at `URLRequest` or `URLSessionConfiguration` level:

```swift
var request = URLRequest(url: url)
request.timeoutInterval = 10
```

## Retry

Retry makes sense for transient errors (network hiccups, 503). Do not retry on:
- 4xx client errors (invalid request won't succeed on retry)
- Mutations that are not idempotent

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

Cancel via `Task.cancel()`. Ongoing `URLSession` tasks are cancelled automatically when the Swift Concurrency task is cancelled.

## Practice Questions

- When does retry make sense and when does it not?
- How do you avoid duplicate requests when users interact quickly?

## Senior Take

Exponential backoff with jitter is preferable to fixed-interval retry in production — it avoids thundering herd when many clients fail simultaneously.

## Exercise

Write `fetchWithRetry(url:maxAttempts:) async throws -> Data` with exponential backoff (1s, 2s, 4s). Only retry on `URLError`, never on 4xx HTTP responses. Write two tests: one where the 2nd attempt succeeds and asserts data is returned, one where all attempts fail and asserts the original error is rethrown. Explain in a comment why POST requests often should NOT be retried.
