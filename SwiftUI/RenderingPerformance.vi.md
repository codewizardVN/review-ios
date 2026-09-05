[English](./RenderingPerformance.md) | [Tiếng Việt](./RenderingPerformance.vi.md)

[← SwiftUI](./README.vi.md)

# Hiệu năng Rendering

## Nguyên nhân thường gặp gây Re-render không cần thiết

- `@ObservedObject` / `@StateObject` publish thay đổi cho property mà view không thực sự dùng
- `@EnvironmentObject` lớn cập nhật thường xuyên
- Tính toán nặng trong `body`
- Thiếu `Equatable` conformance trên view type có thể dùng `.equatable()`

## Nội dung ôn tập

- `equatable()` modifier — bỏ qua re-render nếu input không thay đổi
- Tách view — view nhỏ hơn với observation scope hẹp hơn sẽ re-render ít hơn
- `LazyVStack` / `LazyHStack` — trì hoãn tạo off-screen views
- `List` vs `ScrollView + LazyVStack` — `List` có cell reuse tích hợp sẵn

## Câu hỏi thực hành

- Tại sao view cứ reload không mong muốn?
- Nếu list lớn bị lag, bắt đầu debug từ đâu?

## Câu hỏi luyện tập

- Tại sao một view cứ reload liên tục ngoài ý muốn?
- Nếu một list lớn bị lag, bạn bắt đầu debug từ đâu?

## Góc nhìn Senior

Câu hỏi đầu tiên luôn là: `@Published` property nào thay đổi và view nào đang observe nó? Dùng SwiftUI rendering instrumentation của Xcode hoặc thêm `let _ = Self._printChanges()` trong `body` để trace re-render khi debug.

## Bài tập

Tạo `UserListView` với `@StateObject var viewModel` publish `var users: [User]` và `var selectedTab: Int`. Thêm `Self._printChanges()` vào body của row view. Thay đổi `selectedTab` và quan sát mọi row đều re-render không cần thiết. Sửa bằng cách tách row thành view riêng với observation scope hẹp hơn. Xác nhận rows không còn re-render khi tab thay đổi.
