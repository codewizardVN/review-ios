[English](./RetryTimeout.md) | [Tiếng Việt](./RetryTimeout.vi.md)

[← Networking](./README.vi.md)

# Retry, Timeout và Cancellation

## Timeout

Set ở `URLRequest` (cho từng request) hoặc `URLSessionConfiguration` (cho cả session). Có hai loại timeout khác nhau:
- `timeoutInterval` của `URLRequest` / `timeoutIntervalForRequest` của configuration: thời gian tối đa được phép "im lặng" không nhận thêm dữ liệu nào (mặc định 60 giây). Mỗi lần có dữ liệu đến, đồng hồ đếm lại từ đầu.
- `timeoutIntervalForResource` của configuration: tổng thời gian tối đa cho cả request, kể cả khi dữ liệu vẫn đang đến đều (mặc định 7 ngày).

```swift
var request = URLRequest(url: url)
request.timeoutInterval = 10
```

## Retry

Retry hợp lý cho transient error (mất mạng thoáng qua, 503). Không retry:
- 4xx client error (request sai sẽ không thành công dù retry)
- Mutation không idempotent

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
            // data(from:) không throw với 4xx/5xx, nên phải tự kiểm tra status
            if let http = response as? HTTPURLResponse, !(200..<300).contains(http.statusCode) {
                throw HTTPError.status(http.statusCode)
            }
            return data
        } catch {
            // Bị cancel (user rời màn hình): dừng ngay, không retry
            if error is CancellationError { throw error }
            if let urlError = error as? URLError, urlError.code == .cancelled { throw error }

            // Hết lượt, hoặc lỗi không transient (4xx, DecodingError...): ném lỗi gốc
            guard attempt < attempts, isTransient(error) else { throw error }

            // Backoff 1s, 2s, 4s... Task.sleep tự ném CancellationError nếu bị cancel trong lúc chờ.
            // Production nên thêm jitter (cộng một khoảng ngẫu nhiên) và tôn trọng Retry-After với 429.
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

Cancel qua `Task.cancel()`. Với các API async (`data(from:)`, `data(for:)`...), `URLSession` task đang chạy tự động bị cancel khi Swift Concurrency task bị cancel, và lời gọi `await` ném `URLError(.cancelled)`. Cancellation là cooperative, nên code retry phải nhận ra lỗi này và dừng lại, như ví dụ ở trên.

## Câu hỏi thực hành

- Khi nào retry hợp lý và khi nào không?
- Làm sao tránh duplicate request khi người dùng thao tác nhanh?

## Câu hỏi luyện tập

- Khi nào retry hợp lý và khi nào không?
- Làm sao bạn tránh duplicate request khi user thao tác nhanh?

## Góc nhìn Senior

Exponential backoff với jitter tốt hơn fixed-interval retry trong production — tránh thundering herd khi nhiều client thất bại cùng lúc.

## Đáp án câu hỏi luyện tập

### Khi nào retry hợp lý và khi nào không?

Retry hợp lý khi lỗi có khả năng tự hết (transient) và việc gửi lại request không gây tác dụng phụ; không hợp lý khi lỗi sẽ lặp lại y hệt, hoặc khi request có thể bị thực hiện hai lần.

Nên retry:
- `URLError` như `.timedOut`, `.networkConnectionLost`, `.cannotConnectToHost` — mạng chập chờn.
- HTTP 502, 503, 504 — server tạm quá tải hoặc đang deploy.
- HTTP 429 — nhưng phải chờ đúng theo header `Retry-After`.

Không nên retry:
- Các 4xx khác (400, 403, 404, 422): request sai thì gửi lại vẫn sai. 401 nên đi vào luồng refresh token, không phải retry mù.
- `DecodingError`: payload vẫn y như cũ.
- Cancellation (`CancellationError`, `URLError(.cancelled)`): user đã rời màn hình. Một vòng lặp ngây thơ `catch` mọi error sẽ retry cả khi bị cancel — vì vậy ví dụ trong file kiểm tra hai lỗi này đầu tiên và rethrow ngay.
- Mutation không idempotent (POST tạo đơn hàng, thanh toán) nếu không có idempotency key.
- `.notConnectedToInternet`: retry ngay là vô nghĩa; tốt hơn là bật `waitsForConnectivity` hoặc chờ `NWPathMonitor` báo có mạng.

Khi retry, dùng exponential backoff có jitter, giới hạn số lần và tổng thời gian, để loading không kéo dài vô hạn và không dồn thêm tải lên server đang yếu.

Trade-off: retry che lỗi thoáng qua khỏi mắt user nhưng làm chậm việc báo lỗi thật. Với thao tác user đang chờ trên màn hình, 2–3 lần là đủ; sau đó hiển thị lỗi kèm nút "Thử lại".

### Làm sao bạn tránh duplicate request khi user thao tác nhanh?

Hãy coi mỗi thao tác là một operation có trạng thái "đang chạy", và quyết định rõ cho từng loại: bỏ qua lần bấm thêm, gộp chung vào request đang chạy, hay hủy request cũ.

Ba chiến lược:
- **Bỏ qua (drop)**: nút "Gửi" chuyển sang disabled, hoặc ViewModel giữ cờ `isSubmitting` để lần bấm thứ hai không làm gì. Hợp với mutation.
- **Gộp (coalesce)**: nhiều nơi cùng cần một resource (ví dụ profile) thì dùng chung `Task` đang chạy thay vì tạo request mới.
- **Hủy cái cũ (latest wins)**: ô search gõ liên tục thì cancel `Task` trước, debounce khoảng 300ms, chỉ lấy kết quả mới nhất.

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

Chặn ở client chưa đủ cho các thao tác quan trọng như thanh toán: app có thể gửi request, mất kết nối trước khi nhận response, rồi user bấm thử lại. Vì vậy nên gửi kèm một `Idempotency-Key` (UUID tạo một lần cho mỗi thao tác, giữ nguyên qua các lần gửi lại) để server nhận ra và không xử lý hai lần.

Trade-off: khi coalesce, một caller bị cancel không hủy được request chung (vì `Task` trong dictionary không có structured parent), nên cần cân nhắc nếu request nặng.

## Bẫy phỏng vấn

### `request.timeoutInterval = 10` có nghĩa là request phải xong trong 10 giây?

**Dễ trả lời sai:** "Đúng, quá 10 giây là request fail."

**Nên trả lời:** Đây là idle timeout: request chỉ fail khi không có dữ liệu nào đến trong 10 giây liên tiếp. Một download chậm nhưng đều đặn có thể kéo dài vài phút mà không bao giờ timeout. Giới hạn tổng thời gian là `timeoutIntervalForResource` trên `URLSessionConfiguration` (mặc định 7 ngày). Nếu cần deadline cho cả thao tác, kể cả các lần retry, hãy tự đặt ở tầng gọi, ví dụ cho request "đua" với `Task.sleep` trong một task group.

### `Task.cancel()` có dừng ngay request và vòng retry không?

**Dễ trả lời sai:** "Có, cancel là mọi thứ dừng lập tức."

**Nên trả lời:** Cancellation trong Swift Concurrency là cooperative: nó chỉ đặt một cờ. `URLSession` có tôn trọng cờ này và ném `URLError(.cancelled)`, `Task.sleep` ném `CancellationError`, nhưng nếu vòng retry `catch` mọi error rồi thử lại, nó vẫn gửi request tiếp sau khi đã bị cancel. Phải rethrow ngay khi gặp lỗi cancellation (như ví dụ trong file làm với `CancellationError` và `URLError(.cancelled)`), hoặc kiểm tra `Task.isCancelled` / gọi `try Task.checkCancellation()` trước mỗi lần thử. Ngoài ra `Task { }` unstructured không tự bị cancel khi view biến mất; `.task` modifier của SwiftUI thì có.

### Request POST bị timeout — retry có an toàn không, vì chắc server chưa nhận được?

**Dễ trả lời sai:** "An toàn, timeout nghĩa là request chưa tới server."

**Nên trả lời:** Timeout chỉ nói rằng client không nhận được response kịp; server có thể đã xử lý xong và response bị mất trên đường về. Retry POST lúc đó có thể tạo hai đơn hàng hoặc trừ tiền hai lần. Chỉ retry mutation khi server hỗ trợ idempotency key (header như `Idempotency-Key` giữ nguyên qua các lần thử), hoặc khi thao tác vốn idempotent theo đúng ngữ nghĩa như PUT/DELETE.

## Bài tập

Viết `fetchWithRetry(url:maxAttempts:) async throws -> Data` với exponential backoff (1s, 2s, 4s). Chỉ retry với `URLError`, không retry với 4xx HTTP. Viết hai test: một nơi lần thử thứ 2 thành công và assert data được trả về, một nơi tất cả lần thử thất bại và assert original error được rethrow. Giải thích trong comment tại sao POST request thường KHÔNG nên được retry.
