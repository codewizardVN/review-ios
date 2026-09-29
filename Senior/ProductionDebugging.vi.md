[English](./ProductionDebugging.md) | [Tiếng Việt](./ProductionDebugging.vi.md)

[← Chủ đề Senior](./README.vi.md)

# Debug vấn đề Production

## Quy trình

```text
1. Observe — crash log, tỷ lệ lỗi, báo cáo người dùng
2. Reproduce — có thể reproduce ở local hay staging không?
3. Isolate — build nào, OS version, loại device, phân khúc người dùng?
4. Fix — thay đổi có mục tiêu với blast radius tối thiểu
5. Verify — deploy, theo dõi metrics, xác nhận đã giải quyết
```

## Công cụ

- **Firebase Crashlytics / Sentry** — symbolication và nhóm crash
- **dSYM files** — cần thiết cho crash log có symbol; archive và upload mỗi lần release
- **MetricKit** — app tự nhận báo cáo metric (launch time, hang, memory, số lần bị hệ thống kill) và diagnostic (crash, hang, CPU exception) từ thiết bị người dùng, thường gửi theo ngày
- **Xcode Organizer** — xem crash, hang, energy và các metric do Apple thu thập từ người dùng đồng ý chia sẻ dữ liệu, không cần SDK bên thứ ba
- **TestFlight** — phân phối build có thêm logging hoặc diagnostic cho nhóm tester để reproduce. Lưu ý build TestFlight được ký distribution và thường build theo cấu hình của bước Archive (mặc định là Release) giống bản App Store, nên không attach debugger được

## Vấn đề chỉ xảy ra trong Production

- Race condition xuất hiện dưới tải thật
- Memory pressure trên thiết bị cũ
- Edge case về localization hoặc timezone
- API contract thay đổi không được phát hiện trong development

## Câu hỏi thực hành

- Bạn tiếp cận một crash production ngẫu nhiên như thế nào?

## Câu hỏi luyện tập

- Bạn tiếp cận một crash production ngẫu nhiên như thế nào?

## Góc nhìn senior

Crash production không có đường reproduce đòi hỏi xây dựng giả thuyết từ dữ liệu có sẵn: stack trace, phân phối OS/device, phạm vi app version, cohort người dùng. Thu hẹp không gian giả thuyết trước khi viết bất kỳ fix nào.

## Đáp án câu hỏi luyện tập

### Bạn tiếp cận một crash production ngẫu nhiên như thế nào?

Tôi không bắt đầu bằng sửa code; tôi bắt đầu bằng việc dùng dữ liệu để biến crash "ngẫu nhiên" thành một mẫu hình có điều kiện rõ ràng, rồi mới đặt giả thuyết và fix.

Các bước:

1. **Đánh giá mức độ:** bao nhiêu người dùng bị ảnh hưởng, crash-free rate giảm bao nhiêu, bắt đầu từ version nào. Việc này quyết định cần hotfix gấp hay đưa vào release thường.
2. **Đọc stack trace đã symbolicate** (đảm bảo dSYM đúng build đã được upload): loại exception là gì — `EXC_BREAKPOINT` thường là Swift runtime trap như force unwrap `nil` hay index out of range, `EXC_BAD_ACCESS` là truy cập vùng nhớ không hợp lệ, `0x8badf00d` là watchdog kill vì main thread bị chặn quá lâu. Crash trên main thread hay background thread.
3. **Tìm điểm chung:** OS version, device, app version, locale, trạng thái app (vừa mở từ push, từ background, bộ nhớ thấp). Breadcrumb và log trước crash rất có giá trị.
4. **Đặt giả thuyết và kiểm chứng:** ví dụ crash chỉ trên iOS 16 trong `CartViewController.viewDidLoad` gợi ý khác biệt behavior của API hoặc lifecycle trên iOS 16, hoặc dữ liệu (từ deep link, từ cache) chưa sẵn sàng. Thử reproduce trên máy thật chạy iOS 16 hoặc simulator iOS 16 (nếu Xcode đang dùng còn cài được runtime đó), bật Thread Sanitizer, giả lập mạng chậm bằng Network Link Conditioner.
5. **Nếu chưa reproduce được:** ship fix phòng thủ (bỏ force unwrap, xử lý `nil` an toàn) kèm log hoặc non-fatal event để xác nhận giả thuyết, và dùng feature flag nếu có thể tắt vùng lỗi.
6. **Verify bằng dữ liệu:** crash giảm trên version mới.

Trade-off: fix phòng thủ như `guard let` có thể che giấu bug gốc. Luôn kèm logging để vẫn biết trạng thái bất thường xảy ra bao nhiêu lần và vì sao.

## Bẫy phỏng vấn

### "Crash log toàn địa chỉ hex, không có tên hàm. Bạn làm gì?"

**Dễ trả lời sai:** "Tải dSYM từ App Store Connect vì Apple recompile bitcode." Kiến thức này đã lỗi thời.

**Nên trả lời:** Bitcode đã bị deprecate từ Xcode 14 và App Store không còn nhận bitcode, nên Apple không recompile app nữa; dSYM được tạo khi archive và phải được upload từ chính build đó (thường tự động trong CI, ví dụ script upload-symbols của Crashlytics). Nếu lỡ quên, vẫn có thể lấy dSYM trong file `.xcarchive` đã lưu (Xcode Organizer → Show Package Contents → `dSYMs`) và upload lại. Kiểm tra UUID của dSYM có khớp binary bằng `dwarfdump --uuid`. Nếu dSYM của build đã phát hành bị mất, crash của build đó gần như không thể symbolicate đầy đủ, nên đây là việc phải tự động hóa từ đầu.

### "Bạn reproduce bằng debug build trên máy mình, không thấy crash, vậy là ổn?"

**Dễ trả lời sai:** "Không reproduce được ở debug thì có lẽ là lỗi hiếm, tạm bỏ qua." Debug build khác Release build ở nhiều điểm quan trọng.

**Nên trả lời:** Release build có optimization, timing khác, và không có debugger đi kèm. Một số lỗi chỉ lộ ra khi có optimization và timing thật, ví dụ race condition; watchdog cũng không kill app khi debugger đang attach. Nên thử bằng Release configuration hoặc build TestFlight, trên device cũ, với điều kiện mạng và bộ nhớ giống người dùng thật.

### "Frame đầu tiên trong stack trace là nơi có bug, đúng không?"

**Dễ trả lời sai:** "Đúng, crash ở đâu thì sửa ở đó." Top frame thường chỉ là nơi lỗi bị phát hiện.

**Nên trả lời:** Top frame hay nằm trong system framework hoặc runtime, ví dụ crash trong `objc_msgSend` vì object đã bị giải phóng từ trước — bug thật nằm ở nơi quản lý lifetime của object. Cần xem các thread khác, breadcrumb, và "last exception backtrace" nếu có. Cũng nhớ rằng app bị hệ thống kill vì hết bộ nhớ (jetsam) thường không tạo crash report thông thường; dữ liệu loại này phải tìm qua MetricKit (`MXAppExitMetric` đếm số lần app bị kill vì vượt giới hạn bộ nhớ), Xcode Organizer, hoặc chỉ số "OOM" mà công cụ crash reporting suy đoán.

## Bài tập

Cho một báo cáo Crashlytics cho thấy crash force-unwrap `nil` trong `CartViewController.viewDidLoad` chỉ ảnh hưởng người dùng iOS 16 trên version 2.3.1: viết toàn bộ quy trình debug của bạn — những giả thuyết nào bạn đặt ra, dữ liệu nào cần thu thập tiếp, và chiến lược fix trông như thế nào trước khi reproduce được ở local.
