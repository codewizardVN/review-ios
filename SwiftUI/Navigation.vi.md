[English](./Navigation.md) | [Tiếng Việt](./Navigation.vi.md)

[← SwiftUI](./README.vi.md)

# Navigation

## Nội dung ôn tập

- `NavigationStack` — thay thế `NavigationView` từ iOS 16+
- `NavigationPath` — type-erased stack cho programmatic navigation
- `.navigationDestination(for:)` — data-driven destination mapping
- Sheet, fullScreenCover, popover — modal presentations
- Deep linking qua `NavigationPath` hoặc `openURL`

## Ví dụ

```swift
struct AppView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            FeedView()
                .navigationDestination(for: Item.self) { item in
                    ItemDetailView(item: item)
                }
        }
    }
}
```

## Góc nhìn Senior

Ưu tiên data-driven navigation (`.navigationDestination`) thay vì `NavigationLink(destination:)` inline. Cách này tách rời trigger khỏi destination và cho phép programmatic deep linking mà không cần biết toàn bộ view hierarchy.

## Bài tập

Xây dựng app 3 màn hình dùng `NavigationStack` với `NavigationPath`: List → Detail → Reviews. Thêm nút "Go to Root" trên màn Reviews xóa path bằng `path.removeLast(path.count)`. Sau đó hỗ trợ deep link: khi app launch, pre-populate `NavigationPath` để navigate thẳng đến màn Reviews cho một item cụ thể.
