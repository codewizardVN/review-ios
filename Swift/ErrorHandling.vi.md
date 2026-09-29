[English](./ErrorHandling.md) | [Tiếng Việt](./ErrorHandling.vi.md)

[← Swift Core](./README.vi.md)

# Xử lý lỗi

## Nội dung ôn tập

- `throws`: đánh dấu hàm có thể thất bại; caller bắt buộc phải gọi bằng `try` (và phải ở trong `do-catch` hoặc trong một hàm cũng `throws`).
- `do-catch`: bắt lỗi và xử lý; có thể viết nhiều `catch` với pattern (ví dụ `catch NetworkError.unauthorized`), nhánh `catch` cuối không có pattern nhận biến `error`. Thêm `try?` (lỗi thành `nil`) và `try!` (crash nếu có lỗi).
- Typed domain errors: tự định nghĩa kiểu lỗi (thường là `enum` conform `Error`) mô tả đúng các tình huống thất bại của domain, thay vì ném `NSError` hay chuỗi. Đừng nhầm với tính năng typed throws `throws(MyError)` của Swift 6 (xem bên dưới).
- Ánh xạ các lỗi tầng thấp thành lỗi có ý nghĩa với người dùng: ví dụ tầng network nhận `URLError`/`DecodingError`, chuyển thành `NetworkError.timeout` ở tầng data, rồi tầng UI mới quyết định hiện câu "Mất kết nối, vui lòng thử lại".

## Ví dụ

```swift
enum NetworkError: Error {
    case invalidResponse
    case unauthorized
    case timeout
}
```

## Câu hỏi luyện tập

- Một do-catch đầy đủ xử lý từng case của ParseError (missingField, invalidFormat, unsupportedVersion) với thông báo riêng cho người dùng khác gì so với việc chỉ dùng try?

## Góc nhìn Senior

Tránh để lộ các lỗi infrastructure thô trực tiếp lên UI. Hãy giải thích cách lỗi được chuyển đổi qua các layer.

## Đáp án câu hỏi luyện tập

### Một do-catch đầy đủ xử lý từng case của ParseError (missingField, invalidFormat, unsupportedVersion) với thông báo riêng cho người dùng khác gì so với việc chỉ dùng try?

`try?` biến mọi lỗi thành `nil` và vứt bỏ thông tin lỗi, còn `do-catch` giữ lại lỗi để bạn phân biệt từng case và phản ứng khác nhau cho mỗi case.

Cơ chế: `try? parseConfig(from: data)` trả về `Config?`. Khi kết quả là `nil`, bạn không biết là thiếu field nào, format sai ở đâu, hay version không được hỗ trợ — UI chỉ có thể hiện một câu chung chung. Với `do-catch`, bạn pattern match từng case, lấy luôn associated value (tên field, version) để hiện thông báo cụ thể, log cho team, hoặc chọn cách phục hồi — ví dụ `unsupportedVersion` thì gợi ý người dùng cập nhật app.

Từ Swift 6 có typed throws (SE-0413). Nếu khai báo hàm là `func parseConfig(from data: Data) throws(ParseError) -> Config` và đánh dấu khối `do throws(ParseError)`, compiler biết chắc kiểu lỗi, nên `error` trong `catch` có kiểu `ParseError` (không phải `any Error`) và `switch` có thể exhaustive mà không cần nhánh `default`. Mọi lời gọi `try` trong khối đó phải chỉ throw `ParseError` (ở đây giả định `apply` không throw):

```swift
do throws(ParseError) {
    let config = try parseConfig(from: data)
    apply(config)
} catch {
    switch error {
    case .missingField(let name): show("Thiếu trường \(name)")
    case .invalidFormat(let field, let value): show("\(field) sai định dạng: \(value)")
    case .unsupportedVersion(let v): show("Phiên bản \(v) chưa được hỗ trợ, hãy cập nhật app")
    }
}
```

Với `throws` thường, bạn luôn cần thêm một `catch` chung vì hàm có thể throw bất kỳ `Error` nào. `try?` vẫn hợp lý khi thất bại thật sự chỉ có nghĩa là "không có giá trị", ví dụ đọc cache.

## Bẫy phỏng vấn

### "Swift 6 đã có typed throws, vậy nên dùng throws(MyError) ở mọi nơi?"

**Dễ trả lời sai:** Đúng, typed throws luôn tốt hơn vì an toàn kiểu hơn, nên thay hết `throws` bằng `throws(SomeError)`.

**Nên trả lời:** Chính proposal SE-0413 khuyên `throws` không kèm kiểu vẫn là mặc định. Typed throws hợp với code trong một module hoặc thư viện nhỏ nơi tập lỗi thật sự cố định, với Embedded Swift, hoặc với hàm generic chỉ chuyển tiếp lỗi của closure. Ở API công khai, nó khóa bạn vào một kiểu lỗi: thêm case mới sẽ phá các `switch` exhaustive của caller, và lỗi từ tầng dưới (URLError, DecodingError) phải được bọc lại thủ công.

### "Lỗi throw bên trong Task { } sẽ đi đâu?"

**Dễ trả lời sai:** App sẽ crash, hoặc lỗi tự hiện ra trong console/được báo cho caller.

**Nên trả lời:** Một unstructured `Task { try await ... }` lưu lỗi vào kết quả của chính nó. Nếu không ai `await task.value` (hoặc `task.result`), lỗi bị nuốt âm thầm — không crash, không log. Vì vậy bên trong `Task` nên có `do-catch` riêng để cập nhật UI state hoặc log, thay vì để lỗi lọt ra ngoài.

### "Hiện error.localizedDescription lên UI là đủ đúng không?"

**Dễ trả lời sai:** Đúng, mọi `Error` đều có `localizedDescription` nên chỉ cần hiện nó ra.

**Nên trả lời:** Với một enum tự định nghĩa như `ParseError`, `localizedDescription` chỉ trả về câu chung chung kiểu "The operation couldn't be completed. (App.ParseError error 0.)". Muốn có thông báo tử tế, hãy conform `LocalizedError` và implement `errorDescription` (có thể thêm `recoverySuggestion`). Tốt hơn nữa là tách rõ: tầng domain giữ lỗi có cấu trúc, tầng presentation mới quyết định câu chữ hiển thị.

## Bài tập

Định nghĩa một enum `ParseError` với các case: `missingField(String)`, `invalidFormat(String, String)`, và `unsupportedVersion(Int)`. Viết một function `parseConfig(from data: Data) throws -> Config` throw các lỗi này. Viết call site với một `do-catch` đầy đủ xử lý từng case với một thông báo riêng biệt hướng tới người dùng. Giải thích sự khác biệt so với việc chỉ dùng `try?`.
