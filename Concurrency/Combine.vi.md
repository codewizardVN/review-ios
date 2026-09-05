[English](./Combine.md) | [Tiếng Việt](./Combine.vi.md)

[← Concurrency](./README.vi.md)

# Combine

## Ý chính

Combine là reactive framework của Apple — `Publisher` phát ra giá trị theo thời gian, `Subscriber` nhận giá trị đó, và các operator biến đổi stream ở giữa. `@Published` và `ObservableObject` trong SwiftUI được xây dựng trên nền tảng này.

## Những điều cần nắm

- `Publisher` / `Subscriber` / `Subscription` — ba protocol cốt lõi
- Các operator phổ biến — `map`, `flatMap`, `combineLatest`, `debounce`, `removeDuplicates`
- `@Published` — publish sự thay đổi giá trị, là nền tảng của hầu hết `ObservableObject` view model
- `AnyCancellable` — phải được giữ lại (thường trong `Set<AnyCancellable>`), nếu không subscription sẽ bị hủy ngay lập tức
- Combine vs `async/await` — Combine mô hình hóa một *stream* giá trị theo thời gian; `async/await` mô hình hóa một lần hoàn thành duy nhất. Dùng Combine cho state UI liên tục (search-as-you-type, form validation); dùng `async/await` cho các tác vụ request/response một lần.

## Ví dụ

```swift
final class SearchViewModel: ObservableObject {
    @Published var query: String = ""
    @Published private(set) var results: [String] = []

    private var cancellables = Set<AnyCancellable>()

    init(searchService: SearchService) {
        $query
            .debounce(for: .milliseconds(300), scheduler: DispatchQueue.main)
            .removeDuplicates()
            .flatMap { query in searchService.search(query) }
            .receive(on: DispatchQueue.main)
            .assign(to: \.results, on: self)
            .store(in: &cancellables)
    }
}
```

## Câu hỏi luyện tập

- Tại sao quên lưu `Cancellable` lại khiến subscription âm thầm ngừng hoạt động?
- Khi nào bạn vẫn nên dùng Combine trong codebase đã chuyển hẳn sang `async/await`?

## Góc nhìn Senior

Combine không "chết" chỉ vì `async/await` xuất hiện. `AsyncSequence` bao phủ khá nhiều trường hợp tương tự, nhưng bộ operator của Combine (`debounce`, `combineLatest`, `removeDuplicates`) vẫn trưởng thành hơn cho reactive state UI với nhiều nguồn dữ liệu. Hãy nắm cả hai, và biết lý giải cái nào phù hợp với luồng dữ liệu cụ thể thay vì mặc định chọn cái đang "thời thượng".

## Bài tập

Xây dựng `LoginFormViewModel` với `@Published var email: String` và `@Published var password: String`. Dùng `combineLatest` và `map` để suy ra `@Published private(set) var isValid: Bool` chỉ true khi email chứa "@" và password có từ 8 ký tự trở lên. Nối để trạng thái `disabled` của một button SwiftUI được bind với `!isValid`. Giải thích trong comment tại sao pattern này sẽ khó diễn đạt hơn nếu chỉ dùng `async/await` thuần.
