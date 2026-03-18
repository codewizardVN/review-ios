[English](./ViewLifecycle.md) | [Tiếng Việt](./ViewLifecycle.vi.md)

[← SwiftUI](./README.vi.md)

# Vòng đời View

## Ý chính

SwiftUI views là value type (struct) được tái tạo thường xuyên. Framework so sánh view description và chỉ áp dụng thay đổi thực sự lên render tree — không phải struct instance.

## Nội dung ôn tập

- `onAppear` / `onDisappear` — hook side effect gắn với visibility của view
- `task` modifier — ưu tiên cho async work; tự cancel khi view biến mất
- View identity — structural vs explicit identity (`.id(value)`)
- Khi nào SwiftUI tái tạo vs tái sử dụng view

## Ví dụ

```swift
struct FeedView: View {
    @StateObject private var viewModel = FeedViewModel()

    var body: some View {
        List(viewModel.items) { item in
            ItemRow(item: item)
        }
        .task {
            await viewModel.load()
        }
    }
}
```

## Góc nhìn Senior

Hiểu về identity là chìa khóa. Hai view có cùng type ở cùng vị trí trong hierarchy sẽ chia sẻ state. Thay đổi `.id()` sẽ phá hủy và tái tạo state. Điều này quan trọng khi animate list hoặc reset form field.

## Bài tập

Xây dựng `CountdownView` bắt đầu đếm ngược từ 10 dùng `.task` và `try await Task.sleep`. Xác nhận timer cancel khi navigate away bằng cách wrap sleep trong `withTaskCancellationHandler` in ra "cancelled". Navigate away giữa chừng và xác nhận message xuất hiện. Giải thích trong comment tại sao `.task` được ưu tiên hơn `onAppear` + quản lý task thủ công.
