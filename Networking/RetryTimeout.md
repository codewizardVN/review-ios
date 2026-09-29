[English](./RetryTimeout.md) | [Tiếng Việt](./RetryTimeout.vi.md)

[← Networking](./README.md)

# Retry, Timeout, and Cancellation

## Timeout

Set at the `URLRequest` level (per request) or the `URLSessionConfiguration` level (for the whole session). There are two different kinds of timeout:
- `URLRequest.timeoutInterval` / the configuration's `timeoutIntervalForRequest`: the maximum time allowed with no new data arriving (60 seconds by default). Every time data arrives, the clock restarts.
- The configuration's `timeoutIntervalForResource`: the maximum total time for the whole request, even if data keeps arriving steadily (7 days by default).

```swift
var request = URLRequest(url: url)
request.timeoutInterval = 10
```

## Retry

Retry makes sense for transient errors (network hiccups, 503). Do not retry on:
- 4xx client errors (invalid request won't succeed on retry)
- Mutations that are not idempotent

```swift
enum HTTPError: Error {
    case status(Int)
}

func fetchWithRetry(url: URL, attempts: Int = 3) async throws -> Data {
    precondition(attempts >= 1)
    var attempt = 1
    while true {
        do {
            let (data, response) = try await URLSession.shared.data(from: url)
            // data(from:) does not throw on 4xx/5xx, so check the status yourself
            if let http = response as? HTTPURLResponse, !(200..<300).contains(http.statusCode) {
                throw HTTPError.status(http.statusCode)
            }
            return data
        } catch {
            // Cancelled (the user left the screen): stop immediately, do not retry
            if error is CancellationError { throw error }
            if let urlError = error as? URLError, urlError.code == .cancelled { throw error }

            // Out of attempts, or a non-transient error (4xx, DecodingError...): rethrow the original error
            guard attempt < attempts, isTransient(error) else { throw error }

            // Backoff 1s, 2s, 4s... Task.sleep throws CancellationError by itself if cancelled while waiting.
            // In production, add jitter (a random offset) and honor Retry-After for 429.
            try await Task.sleep(for: .seconds(1 << (attempt - 1)))
            attempt += 1
        }
    }
}

func isTransient(_ error: Error) -> Bool {
    if let urlError = error as? URLError {
        let retryable: [URLError.Code] = [.timedOut, .networkConnectionLost, .cannotConnectToHost]
        return retryable.contains(urlError.code)
    }
    if case HTTPError.status(let code) = error {
        return [502, 503, 504].contains(code)
    }
    return false
}
```

## Cancellation

Cancel via `Task.cancel()`. With the async APIs (`data(from:)`, `data(for:)`...), the ongoing `URLSession` task is cancelled automatically when the Swift Concurrency task is cancelled, and the `await` throws `URLError(.cancelled)`. Cancellation is cooperative, so retry code must recognize this error and stop, as the example above does.

## Practice Questions

- When does retry make sense and when does it not?
- How do you avoid duplicate requests when users interact quickly?

## Senior Take

Exponential backoff with jitter is preferable to fixed-interval retry in production — it avoids thundering herd when many clients fail simultaneously.

## Practice Question Answers

### When does retry make sense and when does it not?

Retry makes sense when the error is likely to go away on its own (transient) and resending the request has no side effects; it does not make sense when the error will repeat exactly, or when the request could end up being performed twice.

Retry on:
- `URLError` such as `.timedOut`, `.networkConnectionLost`, `.cannotConnectToHost` — a flaky network.
- HTTP 502, 503, 504 — the server is temporarily overloaded or deploying.
- HTTP 429 — but wait as instructed by the `Retry-After` header.

Do not retry on:
- Other 4xx (400, 403, 404, 422): a wrong request is still wrong when resent. A 401 should go through the token refresh flow, not a blind retry.
- `DecodingError`: the payload will be the same.
- Cancellation (`CancellationError`, `URLError(.cancelled)`): the user has left the screen. A naive loop that `catch`es every error would retry even after cancellation — that is why the example in this file checks these two errors first and rethrows immediately.
- Non-idempotent mutations (a POST that creates an order, a payment) without an idempotency key.
- `.notConnectedToInternet`: retrying immediately is pointless; better to enable `waitsForConnectivity` or wait for `NWPathMonitor` to report connectivity.

When retrying, use exponential backoff with jitter and cap both the number of attempts and the total time, so loading does not drag on forever and you do not pile more load onto a struggling server.

Trade-off: retry hides transient failures from the user but delays reporting real ones. For an action the user is actively waiting on, 2–3 attempts is enough; after that, show the error with a "Try again" button.

### How do you avoid duplicate requests when users interact quickly?

Treat each action as an operation with an "in flight" state, and decide explicitly per action type: ignore extra taps, join the request already in flight, or cancel the old one.

Three strategies:
- **Drop**: the "Send" button becomes disabled, or the ViewModel keeps an `isSubmitting` flag so the second tap does nothing. Suits mutations.
- **Coalesce**: when several places need the same resource (say, the profile), share the in-flight `Task` instead of starting a new request.
- **Latest wins**: for a search field being typed into, cancel the previous `Task`, debounce around 300ms, and keep only the newest result.

```swift
actor RequestCoalescer {
    private var inFlight: [URL: Task<Data, Error>] = [:]

    func data(from url: URL) async throws -> Data {
        if let task = inFlight[url] { return try await task.value }
        let task = Task { try await URLSession.shared.data(from: url).0 }
        inFlight[url] = task
        defer { inFlight[url] = nil }
        return try await task.value
    }
}
```

Client-side blocking is not enough for critical actions like payments: the app may send the request, lose the connection before the response arrives, and then the user taps retry. So also send an `Idempotency-Key` (a UUID created once per action and kept across resends) so the server recognizes it and does not process it twice.

Trade-off: with coalescing, one caller being cancelled cannot cancel the shared request (the `Task` in the dictionary has no structured parent), so think twice if the request is heavy.

## Interview Traps

### Does `request.timeoutInterval = 10` mean the request must finish within 10 seconds?

**Common wrong answer:** "Yes, after 10 seconds the request fails."

**Better answer:** It is an idle timeout: the request fails only if no data arrives for 10 consecutive seconds. A slow but steady download can run for minutes without ever timing out. The total-time limit is `timeoutIntervalForResource` on `URLSessionConfiguration` (7 days by default). If you need a deadline for the whole operation, including retries, enforce it at the call site, for example by racing the request against `Task.sleep` in a task group.

### Does `Task.cancel()` stop the request and the retry loop immediately?

**Common wrong answer:** "Yes, cancel stops everything instantly."

**Better answer:** Cancellation in Swift Concurrency is cooperative: it only sets a flag. `URLSession` does honor that flag and throws `URLError(.cancelled)`, and `Task.sleep` throws `CancellationError`, but if the retry loop `catch`es every error and tries again, it keeps sending requests after cancellation. Rethrow immediately on cancellation errors (as the example in this file does for `CancellationError` and `URLError(.cancelled)`), or check `Task.isCancelled` / call `try Task.checkCancellation()` before each attempt. Also, an unstructured `Task { }` is not cancelled automatically when the view disappears; SwiftUI's `.task` modifier is.

### A POST request timed out — is it safe to retry, since the server probably never got it?

**Common wrong answer:** "Yes, a timeout means the request never reached the server."

**Better answer:** A timeout only tells you the client did not receive a response in time; the server may have finished processing and the response got lost on the way back. Retrying the POST then may create two orders or charge twice. Only retry mutations when the server supports an idempotency key (a header like `Idempotency-Key` kept the same across attempts), or when the operation is idempotent by definition, like PUT/DELETE used with correct semantics.

## Exercise

Write `fetchWithRetry(url:maxAttempts:) async throws -> Data` with exponential backoff (1s, 2s, 4s). Only retry on `URLError`, never on 4xx HTTP responses. Write two tests: one where the 2nd attempt succeeds and asserts data is returned, one where all attempts fail and asserts the original error is rethrown. Explain in a comment why POST requests often should NOT be retried.
