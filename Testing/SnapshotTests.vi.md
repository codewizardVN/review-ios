[English](./SnapshotTests.md) | [Tiếng Việt](./SnapshotTests.vi.md)

[← Testing](./README.vi.md)

# Snapshot Tests

## Ý tưởng chính

Snapshot test render một view và so sánh với ảnh tham chiếu đã lưu. Chúng tự động phát hiện các thay đổi visual không mong muốn.

## Nội dung cần ôn

- swift-snapshot-testing (Point-Free) — thư viện phổ biến nhất
- Chế độ recording vs asserting
- Testing trên simulator vs device — ảnh khác nhau theo device/OS
- Nên snapshot: components, không phải toàn màn hình

## Ví dụ

```swift
import SnapshotTesting

final class ItemRowSnapshotTests: XCTestCase {
    func test_itemRow_default() {
        let view = ItemRow(item: .fixture())
        assertSnapshot(of: view, as: .image(layout: .fixed(width: 375, height: 80)))
    }
}
```

## Câu hỏi thực hành

- Khi nào snapshot test thực sự có giá trị?

## Góc nhìn senior

Snapshot test có giá trị cao cho design system và reusable component. Giá trị thấp hơn cho màn hình đầy đủ thay đổi thường xuyên. Chạy chúng trong CI trên cấu hình simulator cố định để tránh false positive do khác biệt rendering giữa các máy.

## Bài tập

Thêm snapshot test cho `PriceTagView` hiển thị chuỗi giá có ký hiệu tiền tệ. Test ba biến thể: giá thường, giá khuyến mãi và miễn phí. Sau đó mô tả thiết lập CI cần thiết để giữ cho các test này không sinh false positive trên các máy khác nhau.
