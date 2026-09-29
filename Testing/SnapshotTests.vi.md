[English](./SnapshotTests.md) | [Tiếng Việt](./SnapshotTests.vi.md)

[← Testing](./README.vi.md)

# Snapshot Tests

## Ý tưởng chính

Snapshot test render một view và so sánh với ảnh tham chiếu đã lưu. Chúng tự động phát hiện các thay đổi visual không mong muốn.

## Nội dung cần ôn

- swift-snapshot-testing (Point-Free) — thư viện phổ biến nhất; hỗ trợ cả XCTest và Swift Testing, snapshot được SwiftUI view, `UIView`, `UIViewController` và cả dữ liệu dạng text (ví dụ `.dump`, `.json`).
- Chế độ recording vs asserting: khi record, thư viện ghi ảnh mới làm ảnh tham chiếu (reference); khi assert, nó render lại và so với ảnh đã commit. Từ bản 1.17, chế độ record được cấu hình bằng `withSnapshotTesting(record:)` hoặc biến môi trường `SNAPSHOT_TESTING_RECORD` (xem bẫy phỏng vấn cuối bài).
- Testing trên simulator vs device — ảnh khác nhau theo model máy, phiên bản iOS, scale màn hình và Xcode, nên cả team và CI phải record/verify trên cùng một cấu hình simulator; thường không chạy snapshot test trên device thật.
- Nên snapshot: components, không phải toàn màn hình — component nhỏ ổn định và dùng lại nhiều nơi, còn màn hình đầy đủ đổi thường xuyên nên phải record lại liên tục.

## Ví dụ

```swift
import SnapshotTesting
import SwiftUI
import XCTest
@testable import MyApp

// ItemRow là một SwiftUI View; `layout: .fixed(...)` là tuỳ chọn của strategy
// `.image` cho SwiftUI. View là @MainActor nên test class cũng @MainActor.
@MainActor
final class ItemRowSnapshotTests: XCTestCase {
    func test_itemRow_default() {
        let view = ItemRow(item: .fixture())
        assertSnapshot(of: view, as: .image(layout: .fixed(width: 375, height: 80)))
    }
}
```

## Câu hỏi thực hành

- Khi nào snapshot test thực sự có giá trị?

## Câu hỏi luyện tập

- Khi nào snapshot test mang lại giá trị thật sự?

## Góc nhìn senior

Snapshot test có giá trị cao cho design system và reusable component. Giá trị thấp hơn cho màn hình đầy đủ thay đổi thường xuyên. Chạy chúng trong CI trên cấu hình simulator cố định để tránh false positive do khác biệt rendering giữa các máy.

## Đáp án câu hỏi luyện tập

### Khi nào snapshot test mang lại giá trị thật sự?

Snapshot test có giá trị thật khi UI tương đối ổn định, được dùng lại nhiều nơi, và phải hiển thị đúng ở nhiều biến thể mà mắt người khó kiểm tra hết mỗi lần thay đổi code.

Cơ chế rất đơn giản: test render view (như `ItemRow`) thành ảnh, so từng pixel với ảnh tham chiếu đã commit, và fail nếu khác. Nhờ vậy nó bắt được lỗi mà unit test không thấy: padding lệch, text bị cắt, màu sai trong dark mode, layout vỡ khi Dynamic Type lớn hoặc ngôn ngữ right-to-left.

Những nơi đáng dùng:

- Component của design system: button, badge, cell, `PriceTagView` với các trạng thái giá thường, khuyến mãi, miễn phí.
- Ma trận biến thể: light/dark, nhiều cỡ chữ, nhiều ngôn ngữ, iPhone nhỏ/lớn. Một test có thể sinh nhiều ảnh cho từng tổ hợp.
- Refactor UI (ví dụ chuyển UIKit sang SwiftUI) mà muốn giữ nguyên hình ảnh.

Khi nào ít giá trị: màn hình đầy đủ đang thay đổi thiết kế liên tục, vì mỗi lần sửa phải record lại hàng loạt ảnh và mọi người sẽ bấm chấp nhận mà không nhìn. Snapshot cũng không kiểm tra logic, tương tác hay navigation; nó chỉ nói "hình trông như cũ".

Trade-off: ảnh làm repo nặng và test phụ thuộc môi trường render (simulator, phiên bản iOS, Xcode). Cần chạy trên một cấu hình simulator cố định trong CI và review diff ảnh nghiêm túc trong pull request.

## Bẫy phỏng vấn

### "Snapshot test fail sau khi merge, cách xử lý nhanh là record lại ảnh mới?"

**Dễ trả lời sai:** Đúng, snapshot fail thường chỉ vì UI đổi, cứ record lại rồi commit là xong.

**Nên trả lời:** Record lại mà không xem diff biến snapshot test thành "con dấu đóng sẵn", mất đúng lý do tồn tại của nó. Khi fail, thư viện ghi ra ảnh reference, ảnh mới và ảnh diff; cần mở ra xác định thay đổi đó là cố ý hay regression. Chỉ record lại khi thay đổi đúng là thiết kế mong muốn, và reviewer của pull request nên xem ảnh reference mới như xem code.

### "Tôi record ảnh trên máy mình và commit, sao CI lại fail dù không đổi gì?"

**Dễ trả lời sai:** CI bị lỗi hoặc thư viện có bug, cứ giảm `precision` xuống thấp là hết.

**Nên trả lời:** Kết quả render phụ thuộc vào model simulator, phiên bản iOS runtime, phiên bản Xcode, scale màn hình, font và đôi khi kiến trúc máy, nên ảnh từ máy dev và CI có thể khác vài pixel do anti-aliasing. Cách đúng là cố định một cấu hình (cùng simulator, cùng OS, cùng Xcode) cho cả record và verify, thường là record ngay trên CI hoặc bằng script chung. Có thể dùng `perceptualPrecision` (ví dụ `0.98`) để bỏ qua khác biệt nhỏ mắt người không thấy; hạ `precision` quá thấp sẽ che luôn regression thật.

### "Lần đầu chạy snapshot test thì nó pass, đúng không?"

**Dễ trả lời sai:** Đúng, lần đầu không có gì để so nên test pass, và để record phải đặt biến global `isRecording = true`.

**Nên trả lời:** Với swift-snapshot-testing, khi chưa có ảnh reference, thư viện sẽ ghi ảnh mới và cố ý *fail* test để bạn xem lại ảnh trước khi commit. Mọi lần thư viện ghi ảnh mới xuống đĩa, test đều fail có chủ đích, kể cả khi đang bật record. Cách bật record cũng đã đổi: từ bản 1.17, có bốn chế độ `.missing` (mặc định: chỉ ghi ảnh còn thiếu), `.failed` (ghi đè ảnh của những snapshot fail), `.all` (ghi lại tất cả) và `.never` (không bao giờ ghi). Cấu hình bằng `withSnapshotTesting(record: .all) { ... }` (trong XCTest thường bọc trong `override func invokeTest()`), trait `.snapshots(record:)` của Swift Testing, tham số `record:` của `assertSnapshot` cho từng assertion, hoặc biến môi trường `SNAPSHOT_TESTING_RECORD` (ví dụ `SNAPSHOT_TESTING_RECORD=failed`). Biến global `isRecording` cũ đã deprecated. Trong CI nên dùng `.never`: nếu thiếu ảnh reference thì test fail với thông báo rõ ràng thay vì âm thầm tạo ảnh mới trên máy CI.

## Bài tập

Thêm snapshot test cho `PriceTagView` hiển thị chuỗi giá có ký hiệu tiền tệ. Test ba biến thể: giá thường, giá khuyến mãi và miễn phí. Sau đó mô tả thiết lập CI cần thiết để giữ cho các test này không sinh false positive trên các máy khác nhau.
