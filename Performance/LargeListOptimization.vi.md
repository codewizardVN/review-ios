[English](./LargeListOptimization.md) | [Tiếng Việt](./LargeListOptimization.vi.md)

[← Performance](./README.vi.md)

# Tối ưu List lớn

## Nguyên nhân gốc rễ của List bị lag

1. Cell configuration chậm (tính toán nặng, decode ảnh đồng bộ)
2. Tất cả cell được tạo cùng lúc (không có lazy loading)
3. Reload toàn list không cần thiết thay vì cập nhật dựa trên diff
4. Main thread bị block trong khi scroll

## UIKit

- `UICollectionView` / `UITableView` — cell được reuse qua `dequeueReusableCell`
- `UICollectionViewDiffableDataSource` — apply snapshot để cập nhật có animation và diff
- `UICollectionViewCompositionalLayout` — layout linh hoạt không cần tính frame thủ công
- `prefetchDataSource` — load data trước khi cell hiển thị

## SwiftUI

- `List` — reuse cell tích hợp, ưu tiên dùng thay `ScrollView + ForEach` cho data lớn
- `LazyVStack` bên trong `ScrollView` — defer tạo, nhưng không reuse
- Tránh computed property nặng trong cell view
- Xác định item với `id` ổn định để SwiftUI diff hiệu quả

## Câu hỏi thực hành

- Nếu màn hình scroll kém, bạn kiểm tra gì đầu tiên?

## Góc nhìn senior

Profile trước. Cách sửa phụ thuộc vào nguyên nhân gốc: cell configuration chậm vs allocation quá nhiều vs main thread bị block. Kiểm tra Time Profiler trong khi scroll trước khi viết bất kỳ code tối ưu nào.

## Bài tập

Build `UICollectionView` hiển thị 10.000 item dùng `UICollectionViewDiffableDataSource`. Apply snapshot update khi filter thay đổi. Sau đó chuyển sang SwiftUI và implement cùng list dùng `List` với `id` ổn định. So sánh hiệu năng scroll dùng Time Profiler và ghi nhận sự khác biệt về frame rate.
