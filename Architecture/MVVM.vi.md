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

## Câu hỏi thực hành

- Làm sao nhận biết ViewModel đang trở nên quá lớn?
- Cái gì thuộc ViewModel vs use case layer?

## Câu hỏi luyện tập

- Bạn nhận ra một ViewModel đang phình to quá mức bằng cách nào?
- Cái gì thuộc về ViewModel và cái gì thuộc về tầng use case?

## Góc nhìn Senior

MVVM không tự động có nghĩa là Clean Architecture. ViewModel gọi trực tiếp URLSession vẫn bị tightly coupled. Dùng MVVM cho presentation logic; thêm service/use case layer bên dưới cho business logic.

## Bài tập

Xây dựng `WeatherViewModel` với `@Published var temperature: String`, `@Published var isLoading: Bool`, và `@Published var errorMessage: String?`. Inject `WeatherService` protocol trả về Kelvin thô. ViewModel chuyển đổi sang định dạng "23°C". Viết `FakeWeatherService`. Viết 3 unit test: thành công (format đúng), lỗi service (errorMessage được set), và xác nhận không có UIKit import trong file ViewModel.
