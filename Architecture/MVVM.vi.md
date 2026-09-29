[English](./MVVM.md) | [Tiếng Việt](./MVVM.vi.md)

[← Architecture](./README.vi.md)

# MVVM (Model-View-ViewModel)

## Ý chính

ViewModel chứa presentation logic và expose state để View bind vào. View thụ động — nó render state và chuyển tiếp events.

## Trách nhiệm

- **Model** — data, business rules, domain logic
- **ViewModel** — format model data để hiển thị, xử lý user input, kích hoạt use case
- **View** — render ViewModel output, chuyển tiếp user action

## Ví dụ

```swift
@MainActor
final class FeedViewModel: ObservableObject {
    @Published private(set) var items: [FeedItem] = []
    @Published private(set) var isLoading = false

    private let repository: FeedRepository

    init(repository: FeedRepository) {
        self.repository = repository
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        items = (try? await repository.fetchFeed()) ?? []
    }
}
```

Ví dụ trên dùng `ObservableObject` + `@Published` (Combine), chạy được trên mọi phiên bản iOS mà SwiftUI hỗ trợ. Nếu app target iOS 17+, cách hiện đại là dùng macro `@Observable` (framework Observation): bỏ `ObservableObject` và `@Published`, view chỉ re-render khi đọc đúng thuộc tính bị thay đổi, và view giữ ViewModel bằng `@State` thay vì `@StateObject`. Cấu trúc MVVM (ViewModel giữ state, inject repository qua `init`) không đổi.

## Câu hỏi thực hành

- Làm sao nhận biết ViewModel đang trở nên quá lớn?
- Cái gì thuộc ViewModel vs use case layer?

## Câu hỏi luyện tập

- Bạn nhận ra một ViewModel đang phình to quá mức bằng cách nào?
- Cái gì thuộc về ViewModel và cái gì thuộc về tầng use case?

## Góc nhìn Senior

MVVM không tự động có nghĩa là Clean Architecture. ViewModel gọi trực tiếp URLSession vẫn bị tightly coupled. Dùng MVVM cho presentation logic; thêm service/use case layer bên dưới cho business logic.

## Đáp án câu hỏi luyện tập

### Bạn nhận ra một ViewModel đang phình to quá mức bằng cách nào?

Dấu hiệu rõ nhất là ViewModel bắt đầu làm những việc không phải "màn hình này hiển thị gì và phản ứng với input ra sao".

Các triệu chứng cụ thể:

- `init` nhận quá nhiều dependency (năm, sáu service trở lên), thường là do ViewModel đang tự điều phối business flow.
- Chứa business rule: tính giảm giá, kiểm tra điều kiện đặt hàng, kết hợp dữ liệu từ nhiều repository. Những thứ này sẽ phải viết lại nếu một màn hình khác hay widget cũng cần.
- Gọi thẳng `URLSession`, database hay `UserDefaults` thay vì qua repository.
- Nhiều cờ `Bool` rời rạc như `isLoading`, `isEmpty`, `hasError` có thể mâu thuẫn nhau, thay vì một `enum State`.
- Phục vụ nhiều khu vực độc lập của màn hình (header, danh sách, bộ lọc) trong cùng một class.
- File test cần setup rất dài chỉ để kiểm tra một hành vi nhỏ.

Cách xử lý: đẩy business rule xuống use case/service, tách child ViewModel cho từng section, gom state thành enum. Trade-off là đừng đếm số dòng một cách máy móc: một ViewModel 300 dòng nhưng chỉ lo presentation cho một màn hình phức tạp vẫn ổn. Tách quá sớm tạo thêm object và binding khó theo dõi.

### Cái gì thuộc về ViewModel và cái gì thuộc về tầng use case?

ViewModel giữ presentation logic của một màn hình cụ thể; use case giữ business rule đúng bất kể UI trông thế nào.

ViewModel lo: format dữ liệu để hiển thị (trong bài tập, đổi Kelvin sang chuỗi "23°C"), map lỗi thành `errorMessage` dễ đọc, quản lý `isLoading`, debounce ô tìm kiếm, quyết định nút nào được bật. Những thứ này gắn với một màn hình và thay đổi khi thiết kế thay đổi.

Use case lo: quy tắc nghiệp vụ, ví dụ "đơn hàng trên 500k được free ship", "cảnh báo nắng nóng khi trên 35°C", kết hợp nhiều repository, chính sách cache hay retry. Câu hỏi kiểm tra đơn giản: nếu ngày mai đổi UI từ UIKit sang SwiftUI, hay thêm widget và App Intent, logic này có còn cần không? Nếu còn, nó thuộc use case.

Trade-off: với màn hình CRUD đơn giản, use case chỉ gọi lại repository một dòng, thành boilerplate thuần. Khi đó để ViewModel gọi repository trực tiếp là chấp nhận được, và chỉ tách use case khi business rule thật sự xuất hiện hoặc cần dùng lại ở nhiều nơi.

## Bẫy phỏng vấn

### "`FeedViewModel` là `@MainActor`, vậy `await repository.fetchFeed()` có chạy trên main thread và làm đơ UI không?"

**Dễ trả lời sai:** "Có, mọi thứ trong class `@MainActor` đều chạy trên main thread, nên phải bọc network trong `Task.detached`."

**Nên trả lời:** `await` là điểm suspend: trong lúc chờ, main actor được giải phóng để xử lý việc khác, nên UI không bị block. Code bên trong `fetchFeed()` chạy ở đâu phụ thuộc vào isolation của chính hàm đó, không phải của caller; `URLSession` tự làm việc I/O ngoài main thread. Lưu ý version: từ Swift 6.2, khi bật `NonisolatedNonsendingByDefault` (project mới tạo bằng Xcode 26 thường bật sẵn qua build setting "Approachable Concurrency"), hàm async `nonisolated` sẽ chạy trên actor của caller, nên việc nặng CPU (decode JSON lớn) cần đánh dấu `@concurrent` để chạy ngoài main actor. `Task.detached` hiếm khi là câu trả lời đúng.

### "Trong SwiftUI, tạo ViewModel trong view bằng `@ObservedObject var vm = FeedViewModel(...)` có sao không?"

**Dễ trả lời sai:** "Không sao, `@ObservedObject` và `@StateObject` gần như giống nhau."

**Nên trả lời:** `@ObservedObject` không sở hữu object: mỗi lần view cha re-render và tạo lại struct view, một ViewModel mới được tạo, state và task đang chạy bị mất. Object do view tự tạo phải dùng `@StateObject`; với `@Observable` (iOS 17+) thì dùng `@State`. Gotcha nhỏ: với `@State var vm = FeedViewModel()`, initializer vẫn chạy mỗi lần struct view được khởi tạo lại (SwiftUI chỉ giữ instance đầu tiên), nên đừng đặt side effect trong `init` của ViewModel.

### "`items = (try? await repository.fetchFeed()) ?? []` có vấn đề gì?"

**Dễ trả lời sai:** "Không, gọn và an toàn vì không bao giờ crash."

**Nên trả lời:** `try?` nuốt mất lỗi: lỗi mạng và "feed thật sự rỗng" trông giống hệt nhau với người dùng và với test. Không thể hiển thị thông báo lỗi hay nút thử lại, và test không phân biệt được hai trường hợp. Nên dùng `do/catch` và set state lỗi, hoặc gom vào một `enum State { case loading, loaded([FeedItem]), failed(String) }`. Nếu task bị huỷ, nên bỏ qua `CancellationError` thay vì hiện nó thành lỗi.

## Bài tập

Xây dựng `WeatherViewModel` với `@Published var temperature: String`, `@Published var isLoading: Bool`, và `@Published var errorMessage: String?`. Inject `WeatherService` protocol trả về Kelvin thô. ViewModel chuyển đổi sang định dạng "23°C". Viết `FakeWeatherService`. Viết 3 unit test: thành công (format đúng), lỗi service (errorMessage được set), và xác nhận không có UIKit import trong file ViewModel.
