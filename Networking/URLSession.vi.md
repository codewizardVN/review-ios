[English](./URLSession.md) | [Tiếng Việt](./URLSession.vi.md)

[← Networking](./README.vi.md)

# URLSession

## Ý chính

`URLSession` là HTTP client tiêu chuẩn trên iOS. Với hầu hết app, `URLSession.shared` là đủ. Dùng custom configuration cho timeout, caching và background transfer.

## Nội dung ôn tập

- `URLSession.shared` vs custom `URLSession(configuration:)` — `shared` là singleton dùng cấu hình mặc định, không đổi được configuration và không gắn được delegate; khi cần timeout, cache, header chung hay delegate riêng thì tạo session bằng `URLSession(configuration:delegate:delegateQueue:)`.
- `data(from:)` / `data(for:)` — API async/await (iOS 15+), trả về `(Data, URLResponse)`; `data(for:)` nhận `URLRequest` khi cần đặt method, header hoặc body.
- `URLSessionConfiguration` — `.default` (có cache và cookie trên disk), `.ephemeral` (chỉ giữ trong memory, không ghi gì xuống disk), `.background(withIdentifier:)`; các thuộc tính hay dùng: `timeoutIntervalForRequest`, `requestCachePolicy`, `urlCache`, `waitsForConnectivity` (chờ có mạng thay vì fail ngay).
- Background sessions — `URLSessionConfiguration.background(withIdentifier:)`: hệ thống thực hiện download/upload ở process riêng, tiếp tục cả khi app bị suspend; phải dùng delegate (xem bẫy bên dưới).
- `URLRequest` — method, headers, body, timeout cho từng request; header đặt trên request được ưu tiên hơn header chung trong `httpAdditionalHeaders` của configuration.

## Ví dụ

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

## Câu hỏi luyện tập

- Tại sao việc inject URLSession qua init lại giúp bạn test được fetch(_:from:) của một APIClient generic bằng URLProtocol stub cho cả trường hợp decode JSON hợp lệ lẫn trường hợp status non-200 ném ra APIError.invalidResponse?

## Góc nhìn Senior

Inject `URLSession` như một dependency — giúp client testable mà không cần hit real network. Dùng `URLProtocol` subclass để intercept request trong test.

## Đáp án câu hỏi luyện tập

### Tại sao việc inject URLSession qua init lại giúp bạn test được fetch(_:from:) của một APIClient generic bằng URLProtocol stub cho cả trường hợp decode JSON hợp lệ lẫn trường hợp status non-200 ném ra APIError.invalidResponse?

Vì khi `URLSession` được truyền vào qua `init`, test có thể đưa vào một session riêng có `protocolClasses` chứa `URLProtocol` stub, nên mọi request của `fetch(_:from:)` bị chặn lại ngay trong process và không bao giờ ra mạng thật.

Cơ chế: URL Loading System hỏi lần lượt các `URLProtocol` trong configuration xem class nào "nhận" request (`canInit(with:)`). Stub nhận hết, rồi tự tạo `HTTPURLResponse` với status code và `Data` mà test muốn. Code production của `APIClient` không đổi gì — vẫn gọi `session.data(from:)`, vẫn kiểm tra `statusCode == 200`, vẫn decode. Vì vậy một test trả về JSON hợp lệ kèm 200 để kiểm tra decode, test còn lại trả về 500 để assert `APIError.invalidResponse` được throw.

```swift
let config = URLSessionConfiguration.ephemeral
config.protocolClasses = [StubURLProtocol.self]
let client = APIClient(session: URLSession(configuration: config))
```

Nếu `APIClient` dùng cứng `URLSession.shared`, bạn chỉ còn cách gọi `URLProtocol.registerClass` ở mức global — ảnh hưởng tới mọi test khác đang chạy cùng lúc.

Trade-off: `StubURLProtocol` thường giữ handler trong một biến `static`, nên với Swift Testing (chạy song song mặc định) cần đánh dấu suite `.serialized` hoặc lưu handler theo URL. Nếu chỉ muốn test logic mapping mà không quan tâm HTTP, một protocol `HTTPClient` nhỏ để mock có khi đơn giản hơn.

## Bẫy phỏng vấn

### `data(from:)` có throw khi server trả về 404 hoặc 500 không?

**Dễ trả lời sai:** "Có, request lỗi thì `try await` sẽ throw." Nhiều người nghĩ HTTP status lỗi cũng được coi là lỗi như `URLError`.

**Nên trả lời:** Không. `URLSession` chỉ throw khi lỗi ở tầng transport (mất mạng, timeout, cancel, lỗi TLS…) dưới dạng `URLError`. Response 404 hay 500 vẫn là một response HTTP hợp lệ, nên bạn nhận về `(data, response)` bình thường và phải tự kiểm tra `statusCode` — đó là lý do `APIClient` có `guard http.statusCode == 200`. Thực tế nên chấp nhận cả dải `200..<300` thay vì chỉ đúng 200.

### Tạo một `URLSession(configuration:delegate:delegateQueue:)` mới cho mỗi request có sao không?

**Dễ trả lời sai:** "Không sao, session nhẹ, dùng xong để ARC tự giải phóng."

**Nên trả lời:** Session giữ strong reference tới delegate cho đến khi bị invalidate, nên nếu không gọi `finishTasksAndInvalidate()` hoặc `invalidateAndCancel()` thì cả session lẫn delegate bị leak. Ngoài ra mỗi session có connection pool, cache và cookie riêng, nên tạo mới liên tục làm mất connection reuse (HTTP/2, TLS resumption) và chậm hơn. Nên tạo vài session sống lâu, chia theo nhu cầu cấu hình, rồi inject chúng.

### Background session có dùng được `try await session.data(from:)` như session thường không?

**Dễ trả lời sai:** "Được, chỉ cần đổi configuration sang `.background(withIdentifier:)` là request tiếp tục chạy khi app bị suspend."

**Nên trả lời:** Background session được thiết kế quanh delegate: API dùng completion handler bị từ chối ngay lúc runtime, và các async convenience method cũng không phải cách dùng đúng, vì transfer phải tiếp tục khi process của app không còn chạy. Hệ thống thực hiện download task và upload task (từ file) ở process riêng, rồi có thể relaunch app để gọi `application(_:handleEventsForBackgroundURLSession:completionHandler:)` (hoặc `.backgroundTask(.urlSession)` trong SwiftUI). Request API bình thường thì dùng default session; background session chỉ dành cho transfer lớn cần sống sót qua việc app bị suspend hoặc bị hệ thống terminate.

## Bài tập

Xây dựng generic `APIClient` với `func fetch<T: Decodable>(_ type: T.Type, from url: URL) async throws -> T`. Inject `URLSession` qua `init`. Viết hai test dùng `URLProtocol` stub: một trả về JSON hợp lệ và assert decode đúng, một trả về status non-200 và assert `APIError.invalidResponse` được throw.
