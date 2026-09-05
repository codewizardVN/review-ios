[English](./StateManagement.md) | [Tiếng Việt](./StateManagement.vi.md)

[← SwiftUI](./README.vi.md)

# Quản lý State

## Tổng quan Property Wrappers

| Wrapper | Sở hữu state? | Nguồn |
|---|---|---|
| `@State` | Có | Local trong view này |
| `@Binding` | Không | Truyền vào từ parent |
| `@StateObject` | Có | Sở hữu object lifetime |
| `@ObservedObject` | Không | Object được sở hữu bởi nơi khác |
| `@EnvironmentObject` | Không | Inject từ ancestor |

## Nội dung ôn tập

- `@State` — local value state đơn giản; SwiftUI sở hữu nó
- `@Binding` — tham chiếu hai chiều đến state của parent
- `@StateObject` — tạo và sở hữu `ObservableObject`; tồn tại qua view re-creation
- `@ObservedObject` — subscribe vào `ObservableObject` được sở hữu bởi nơi khác
- `@EnvironmentObject` — object inject qua `.environmentObject()`

## Điểm khác biệt quan trọng: `@StateObject` vs `@ObservedObject`

```swift
// Đúng: view này sở hữu view model
struct FeedView: View {
    @StateObject private var viewModel = FeedViewModel()
}

// Đúng: parent tạo ra, view này chỉ observe
struct FeedView: View {
    @ObservedObject var viewModel: FeedViewModel
}
```

Dùng `@ObservedObject` khi view đáng lẽ phải sở hữu object sẽ khiến object bị tái tạo mỗi lần parent re-render.

## Câu hỏi thực hành

- Khi nào nên dùng `@StateObject` thay vì `@ObservedObject`?
- Khi nào `EnvironmentObject` phù hợp, và khi nào là lạm dụng?

## Câu hỏi luyện tập

- Khi nào nên dùng @StateObject thay vì @ObservedObject?
- Khi nào EnvironmentObject phù hợp, và khi nào là lạm dụng?

## Góc nhìn Senior

Luồng dữ liệu một chiều: state đi xuống qua binding và environment, events đi lên qua callback hoặc view model method. Giữ nhất quán chiều này ngăn subtle re-render bugs.

## Bài tập

Xây dựng parent `ShoppingCartView` với `@State var items: [CartItem]`. Tạo child `CartItemRow` nhận `@Binding<CartItem>` để toggle `isSelected`. Thêm `@StateObject var viewModel = CartViewModel()` trong parent. Navigate sang detail screen và quay lại — xác nhận `@StateObject` KHÔNG bị tái tạo bằng cách thêm `init() { print("CartViewModel init") }`. Giải thích điều gì xảy ra nếu dùng `@ObservedObject`.
