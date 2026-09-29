[English](./Combine.md) | [Tiếng Việt](./Combine.vi.md)

[← Concurrency](./README.vi.md)

# Combine

## Ý chính

Combine là reactive framework của Apple — `Publisher` phát ra giá trị theo thời gian, `Subscriber` nhận giá trị đó, và các operator biến đổi stream ở giữa. `@Published` và `ObservableObject` trong SwiftUI được xây dựng trên nền tảng này.

## Những điều cần nắm

- `Publisher` / `Subscriber` / `Subscription` — ba protocol cốt lõi: publisher mô tả nguồn giá trị (kèm kiểu `Output` và `Failure`), subscriber nhận giá trị, còn subscription là "sợi dây" nối hai bên, qua đó subscriber yêu cầu số lượng giá trị (back-pressure) và có thể `cancel()`.
- Các operator phổ biến — `map`, `flatMap`, `switchToLatest`, `combineLatest`, `debounce`, `removeDuplicates`. `flatMap` giữ mọi publisher bên trong cùng chạy; `map` + `switchToLatest` chỉ giữ publisher mới nhất và cancel cái cũ.
- `@Published` — publish sự thay đổi giá trị, là nền tảng của hầu hết `ObservableObject` view model
- `AnyCancellable` — phải được giữ lại (thường trong `Set<AnyCancellable>`), nếu không subscription sẽ bị hủy ngay lập tức
- Combine vs `async/await` — Combine mô hình hóa một *stream* giá trị theo thời gian; `async/await` mô hình hóa một lần hoàn thành duy nhất. Dùng Combine cho state UI liên tục (search-as-you-type, form validation); dùng `async/await` cho các tác vụ request/response một lần.

## Ví dụ

```swift
protocol SearchService {
    func search(_ query: String) -> AnyPublisher<[String], Never>
}

@MainActor
final class SearchViewModel: ObservableObject {
    @Published var query: String = ""
    @Published private(set) var results: [String] = []

    init(searchService: SearchService) {
        $query
            .debounce(for: .milliseconds(300), scheduler: DispatchQueue.main)
            .removeDuplicates()
            .map { query in searchService.search(query) } // mỗi query -> một publisher
            .switchToLatest()                             // cancel request cũ khi có query mới
            .receive(on: DispatchQueue.main)
            .assign(to: &$results)                        // không retain cycle, không cần store(in:)
    }
}
```

Hai lựa chọn quan trọng trong ví dụ này (`switchToLatest` thay vì `flatMap`, `assign(to: &$results)` thay vì `assign(to:on: self)`) được giải thích trong phần Bẫy phỏng vấn.

## Câu hỏi luyện tập

- Tại sao quên lưu `Cancellable` lại khiến subscription âm thầm ngừng hoạt động?
- Khi nào bạn vẫn nên dùng Combine trong codebase đã chuyển hẳn sang `async/await`?

## Góc nhìn Senior

Combine không "chết" chỉ vì `async/await` xuất hiện. `AsyncSequence` bao phủ khá nhiều trường hợp tương tự, nhưng bộ operator của Combine (`debounce`, `combineLatest`, `removeDuplicates`) vẫn trưởng thành hơn cho reactive state UI với nhiều nguồn dữ liệu. Hãy nắm cả hai, và biết lý giải cái nào phù hợp với luồng dữ liệu cụ thể thay vì mặc định chọn cái đang "thời thượng".

## Đáp án câu hỏi luyện tập

### Tại sao quên lưu `Cancellable` lại khiến subscription âm thầm ngừng hoạt động?

Vì `AnyCancellable` tự gọi `cancel()` trong `deinit`: nếu không ai giữ nó, nó bị giải phóng ngay sau câu lệnh và subscription bị hủy theo.

Cơ chế: `sink` và `assign(to:on:)` trả về một `AnyCancellable`, đại diện cho cả chuỗi subscription. Chuỗi đó chỉ sống chừng nào có người giữ strong reference tới `AnyCancellable`. Nếu bạn gán nó cho biến local, hoặc bỏ qua giá trị trả về, thì khi ra khỏi scope (thường là cuối `init`), ARC giải phóng nó, `cancel()` được gọi và publisher ngừng gửi giá trị. Không có lỗi hay crash nào, chỉ là UI không bao giờ cập nhật, nên rất khó debug. Compiler có cảnh báo "result unused" nhưng dễ bị bỏ qua.

Đây là thiết kế có chủ đích: lifetime của subscription gắn với lifetime của object sở hữu nó. Cách thường dùng là khai báo `private var cancellables = Set<AnyCancellable>()` trong view model và gọi `.store(in: &cancellables)`, nên subscription sống bằng view model và tự hủy khi view model bị giải phóng, không cần hủy thủ công. Riêng `assign(to: &$results)` như trong `SearchViewModel` không trả về cancellable: subscription được gắn thẳng vào property `@Published` và sống cùng nó.

```swift
$query.sink { print($0) }                         // hủy ngay (chỉ kịp in giá trị hiện tại)
$query.sink { print($0) }.store(in: &cancellables) // sống cùng view model
```

Lưu ý ngược lại: giữ cancellable ở nơi sống lâu hơn cần thiết (ví dụ singleton) sẽ giữ subscription và các closure của nó quá lâu.

### Khi nào bạn vẫn nên dùng Combine trong codebase đã chuyển hẳn sang `async/await`?

Nên dùng Combine khi bài toán là một stream giá trị liên tục cần các operator theo thời gian hoặc kết hợp nhiều nguồn, và khi framework bạn dùng vẫn nói "ngôn ngữ" Combine.

Cụ thể:
- Operator theo thời gian: `debounce`, `throttle` cho search-as-you-type như `SearchViewModel`.
- Kết hợp nhiều nguồn: `combineLatest` cho form validation như `LoginFormViewModel` trong bài tập, `merge` nhiều event stream.
- API hệ thống trả publisher: `NotificationCenter.publisher`, `Timer.publish`, KVO `publisher(for:)`, và `ObservableObject`/`@Published` cho app còn hỗ trợ iOS dưới 17.

`async/await` mô hình hóa một kết quả duy nhất. `AsyncSequence` mô hình hóa stream, nhưng thư viện chuẩn không có sẵn `debounce` hay `combineLatest`; bạn cần package `swift-async-algorithms` hoặc tự viết. Hai thế giới vẫn nối được với nhau: `publisher.values` (iOS 15+) biến publisher thành `AsyncSequence` để dùng với `for await`.

Trade-off: Combine gần như không được thiết kế lại cho strict concurrency của Swift 6 (nhiều publisher và operator không `Sendable`, và Combine không biết gì về actor isolation, nên bạn thường phải tự `receive(on:)` về main), và từ iOS 17 `@Observable` thay thế `ObservableObject` mà không dùng Combine. Code mới nên giữ Combine ở những chỗ nhỏ thật sự cần operator của nó, thay vì làm kiến trúc chính.

## Bẫy phỏng vấn

### "Nếu `SearchViewModel` viết `.assign(to: \.results, on: self).store(in: &cancellables)` thay vì `.assign(to: &$results)` thì có vấn đề gì không?"

**Dễ trả lời sai:** "Không, hai cách như nhau, đều là cách chuẩn để bind kết quả vào property." Cách viết `on: self` tạo ra một retain cycle.

**Nên trả lời:** `assign(to:on:)` giữ strong reference tới object `on:`, và cancellable lại được lưu trong `self.cancellables`, nên `self` giữ subscription và subscription giữ `self`, view model không bao giờ được giải phóng (subscription cũng không bao giờ bị hủy). Vì vậy ví dụ dùng `assign(to: &$results)` (iOS 14+): nó gắn lifetime vào chính `@Published` property, không tạo cycle và không cần `store(in:)`. Nếu cần logic phức tạp hơn thì dùng `sink` với `[weak self]`.

### "Nếu `SearchViewModel` dùng `flatMap` thay cho `map` + `switchToLatest()`, kết quả có luôn khớp với query cuối cùng không?"

**Dễ trả lời sai:** "Có, `debounce` đã lọc bớt, nên kết quả hiển thị là của query cuối." `debounce` chỉ giảm số request, không cancel request cũ.

**Nên trả lời:** `flatMap` giữ mọi publisher bên trong còn sống, nên request của "ab" và "abc" có thể chạy song song, và nếu "ab" về sau thì UI hiển thị kết quả cũ (stale). Vì vậy ví dụ dùng `map` sang publisher rồi `switchToLatest()`: operator này cancel publisher trước mỗi khi có giá trị mới, nên chỉ kết quả của query mới nhất được gán vào `results`. Đây là phiên bản Combine của pattern `task?.cancel()` trong bài Task.

### "Trong `sink` của `$query`, đọc `self.query` có ra giá trị mới không?"

**Dễ trả lời sai:** "Có, property đã thay đổi thì mới publish." Thực tế `@Published` phát trong `willSet`.

**Nên trả lời:** `@Published` gửi giá trị mới **trước** khi property được gán, nên trong `sink`, `self.query` vẫn là giá trị cũ. Luôn dùng giá trị closure nhận vào thay vì đọc lại property. Bug này hay xuất hiện khi `sink` gọi một method khác đọc nhiều property của view model cùng lúc.

## Bài tập

Xây dựng `LoginFormViewModel` với `@Published var email: String` và `@Published var password: String`. Dùng `combineLatest` và `map` để suy ra `@Published private(set) var isValid: Bool` chỉ true khi email chứa "@" và password có từ 8 ký tự trở lên. Gán kết quả bằng `assign(to: &$isValid)` để tránh retain cycle. Nối để trạng thái `disabled` của một button SwiftUI được bind với `!isValid`. Giải thích trong comment tại sao pattern này sẽ khó diễn đạt hơn nếu chỉ dùng `async/await` thuần.
