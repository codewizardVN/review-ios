[English](./CrashReportingAnalytics.md) | [Tiếng Việt](./CrashReportingAnalytics.vi.md)

[← Chủ đề cấp Senior](./README.vi.md)

# Crash Reporting và Analytics

## Ý chính

Một SDK crash reporting/analytics là hạ tầng production, không phải một thư viện import cho có. Câu hỏi cấp senior xoay quanh tính đúng đắn của symbolication, kỷ luật schema sự kiện, và privacy — không phải dashboard vendor nào đẹp hơn.

## Những điều cần nắm

- Pipeline symbolication — upload dSYM (thủ công hoặc qua script build-phase), khớp UUID dSYM với đúng build đã crash; dSYM sai hoặc thiếu biến crash report thành các địa chỉ bộ nhớ không đọc được
- Crash-free rate như một release gate — theo dõi phần trăm user/session không crash theo từng version, và ngưỡng nào chặn không cho rollout tiếp tục
- Symbolicate cục bộ vs server-side — Xcode Organizer (hoặc `atos`/`symbolicatecrash` trên máy dev) chỉ symbolicate được khi máy đó có đúng dSYM, và Organizer chỉ nhận crash từ user đã đồng ý chia sẻ dữ liệu với developer; khi có nhiều version và nhiều người cùng điều tra, cách này không scale. Crash reporting server-side (Crashlytics, Sentry…) symbolicate tự động cho mọi report, với điều kiện dSYM đã được upload — vì vậy pipeline CI nên tự động upload dSYM ở mỗi lần archive
- Breadcrumb và log non-fatal — ghi lại dấu vết các hành động/state gần nhất của user trước một crash hoặc lỗi đã handle, để report có ngữ cảnh ngoài stack trace
- Kỷ luật schema sự kiện — tên event có version và payload có kiểu, tránh property free-text làm phân mảnh analytics ("purchase_completed" vs "PurchaseComplete" vs "purchase-done" đều nghĩa giống nhau)
- Sampling và chi phí — event tần suất cao (ví dụ vị trí scroll) thường cần sampling hoặc gộp phía client; gửi mọi raw event thường là gánh nặng chi phí và privacy chứ không phải lợi ích
- Ranh giới privacy — cái gì không được đưa vào payload event (PII, vị trí chính xác, nội dung free-text của user) và điều đó ràng buộc thiết kế schema ra sao, gắn với những gì privacy manifest và nutrition label đã khai
- Ngưỡng alert — bộ phát hiện đột biến trên crash rate hay một metric funnel quan trọng, được tinh chỉnh để vừa tránh alert fatigue vừa không bỏ lỡ regression thật

## Ví dụ

```swift
// Tệ: free-text, không version, không ngữ cảnh
Analytics.log("bought item")

// Tốt hơn: có kiểu, mang ngữ cảnh cho một "lý do" mà không có PII.
// (Tên event và schema version được định nghĩa tập trung trong enum event, lớp Analytics tự gắn vào payload.)
Analytics.log(event: .purchaseCompleted(
    sku: "premium_monthly",
    priceTierCents: 999,
    source: .paywallVariantB
))
```

## Câu hỏi luyện tập

- Tại sao một dSYM bị thiếu quan trọng hơn một dòng comment code bị thiếu?
- Tại sao "crash-free users" thường là release gate tốt hơn số crash thô?
- Tại sao tên event analytics nên được review như một API, chứ không thêm tùy tiện theo từng feature?

## Góc nhìn Senior

Đây là chỗ mà "chúng tôi đã cài Crashlytics" và "chúng tôi thực sự hành động được dựa trên tín hiệu production" khác nhau. Câu trả lời tốt mô tả một sự cố mà nợ symbolication hoặc schema event đã thực sự làm chậm việc debug — một crash report không đọc được, một metric không ai tin tưởng vì ba team log cùng một event khác nhau — và quy trình nào (review schema, tự động upload dSYM trong CI, release gate gắn với crash-free rate) đã fix nó một cách có hệ thống thay vì chỉ vá tạm.

## Đáp án câu hỏi luyện tập

### Tại sao một dSYM bị thiếu quan trọng hơn một dòng comment code bị thiếu?

Vì thiếu dSYM thì crash report từ production chỉ còn là một dãy địa chỉ bộ nhớ, và đó thường là dữ liệu duy nhất bạn có về một bug không tái hiện được ở máy dev.

Bản release được build với symbol bị strip khỏi binary để nhỏ và khó reverse. Tên hàm, tên file và số dòng nằm trong file dSYM tách riêng. Khi app crash, thiết bị chỉ ghi lại địa chỉ kiểu `0x1004a3f2c`; server crash reporting dùng dSYM để dịch địa chỉ đó thành `CheckoutViewModel.submit() CheckoutViewModel.swift:88`.

Điểm then chốt là dSYM phải khớp UUID với đúng build đã crash. Build lại cùng commit thường không tái tạo được đúng binary đó (khác toolchain, đường dẫn, setting… là ra UUID khác), nên đừng trông cậy vào việc build lại. Nếu bạn không lưu dSYM từ archive đã upload lên App Store, crash của version đó mất khả năng đọc vĩnh viễn, dù bạn có toàn bộ source.

Comment bị thiếu thì khác: ảnh hưởng tới người đọc code, nhưng có thể viết bổ sung bất cứ lúc nào và không làm mất dữ liệu production.

Cách làm đúng là để CI tự upload dSYM ngay sau mỗi archive, và lưu trữ file `.xcarchive` cho mỗi build phát hành. Trade-off: dSYM chứa thông tin cấu trúc code, nên chỉ upload tới dịch vụ bạn tin tưởng và kiểm soát quyền truy cập.

### Tại sao "crash-free users" thường là release gate tốt hơn số crash thô?

Vì crash-free users là tỷ lệ đã chuẩn hóa theo số người dùng version đó, nên so sánh được giữa các version, còn số crash thô tăng giảm theo số lượng user chứ không theo chất lượng.

Trong phased release, ngày đầu chỉ khoảng 1% user bật tự động cập nhật nhận version mới, ngày thứ bảy là 100%. Số crash thô của version mới chắc chắn tăng dần chỉ vì có thêm người dùng, dù code không tệ đi. Ngược lại, 50 crash có thể là 50 user khác nhau hoặc một user bị crash loop 50 lần. Tỷ lệ "99,6% user không gặp crash" trả lời đúng câu hỏi của release gate: version này có làm bao nhiêu phần trăm người dùng gặp sự cố hay không.

Gate thực tế thường là: dừng rollout nếu crash-free users thấp hơn version trước quá một ngưỡng, ví dụ 0,3 điểm phần trăm, sau khi đã đủ số session tối thiểu để kết luận.

Trade-off:

- Crash-free users che mất tần suất: một user crash loop chỉ tính là một. Nên theo dõi thêm crash-free sessions.
- Với SDK crash reporting bên thứ ba, nó thường không gồm hang, bị kill do hết bộ nhớ, hay bị watchdog kill (xem bẫy phỏng vấn bên dưới); cần MetricKit hoặc Xcode Organizer để thấy các loại này.
- Với app ít user, tỷ lệ dao động mạnh; cần ngưỡng mẫu tối thiểu.

### Tại sao tên event analytics nên được review như một API, chứ không thêm tùy tiện theo từng feature?

Vì event là một hợp đồng dữ liệu có nhiều bên tiêu thụ, và sau khi ship thì bạn không thể sửa những version app cũ đang tiếp tục gửi event đó.

Một event như `purchase_completed` được dùng bởi dashboard của product, báo cáo doanh thu, mô hình dự đoán, và experiment. Nếu mỗi feature tự đặt tên, bạn sẽ có `purchase_completed`, `PurchaseComplete`, `purchase-done`, và không ai biết con số nào đúng. Giống API, event có những đặc điểm sau:

- Khó đổi: app cũ vẫn chạy trên máy user nhiều tháng, tiếp tục gửi tên cũ. Đổi tên nghĩa là phải map cả hai mãi mãi.
- Có kiểu dữ liệu: `priceTierCents: Int` hay `price: "9.99$"` quyết định có tính tổng được không.
- Có ràng buộc privacy: một property free-text có thể vô tình chứa email hay địa chỉ của user.

Cách làm: định nghĩa event bằng enum có kiểu như ví dụ `.purchaseCompleted(sku:priceTierCents:source:)`, có một tracking plan chung, và event mới phải được review trong PR như thay đổi API.

Trade-off: quy trình review làm chậm việc thêm event thử nghiệm. Có thể cho phép một namespace `debug_` hoặc `exp_` với vòng đời ngắn, không được dùng cho báo cáo chính thức.

## Bẫy phỏng vấn

### "Mất dSYM thì tải lại từ App Store Connect là được?"

**Dễ trả lời sai:** Được, Apple build lại từ bitcode nên luôn có dSYM để tải trong App Store Connect.

**Nên trả lời:** Kiến thức này đã cũ. Nút "Download dSYM" trong App Store Connect chỉ có ý nghĩa với app bitcode, vì khi đó Apple recompile và sinh dSYM mới. Bitcode bị deprecate từ Xcode 14 (App Store không nhận build bitcode nữa), App Store không còn recompile app, nên dSYM duy nhất là cái Xcode tạo ra lúc bạn archive. Nếu không lưu archive hoặc không upload dSYM lúc đó, bạn không lấy lại được. CI nên upload dSYM ngay sau bước archive và giữ `.xcarchive` cho mỗi build phát hành.

### "SDK crash reporting bắt được mọi lần app bị tắt đột ngột không?"

**Dễ trả lời sai:** Có, Crashlytics hay Sentry cài signal handler nên mọi lần app chết đều có report.

**Nên trả lời:** Signal handler chỉ chạy khi process còn cơ hội chạy code. Khi hệ thống kill app vì hết bộ nhớ (jetsam, gửi SIGKILL không bắt được) hoặc watchdog kill vì main thread bị block quá lâu lúc launch hay lúc chuyển trạng thái (mã `0x8badf00d`), app không có cơ hội ghi report; SDK chỉ có thể đoán gián tiếp ở lần mở sau (ví dụ Sentry có tính năng "watchdog termination": suy ra lần trước app chết ở foreground mà không có crash). MetricKit bổ sung phần này: `MXCrashDiagnostic` (kèm call stack và termination reason), `MXHangDiagnostic` cho hang, và `MXAppExitMetric` đếm số lần app bị terminate theo từng lý do (hết bộ nhớ, watchdog, crash…). Từ iOS 15, diagnostic payload (crash, hang…) được gửi ngay — với crash thì là ở lần mở app kế tiếp — thay vì gộp vào payload 24 giờ như iOS 14; còn metric payload thì vẫn gửi theo ngày.

### "Hash email trước khi gửi analytics thì không còn là PII nữa phải không?"

**Dễ trả lời sai:** Đúng, hash SHA-256 là đã ẩn danh nên có thể gửi tự do và không cần khai trong nutrition label.

**Nên trả lời:** Hash của email vẫn là một identifier ổn định: ai có cùng email đều tính ra cùng hash và liên kết được dữ liệu giữa các hệ thống. Đó là dữ liệu định danh, phải khai trong nutrition label, và nếu dùng để liên kết với dữ liệu của công ty khác nhằm quảng cáo thì là tracking, cần xin phép qua ATT. Cách an toàn là không gửi identifier của user trong event trừ khi thật sự cần, và dùng ID nội bộ ngẫu nhiên nếu phải nối các session.

## Bài tập

Thiết kế rollout crash-reporting và analytics cho một luồng checkout mới. Nêu rõ: những event non-fatal nào bạn sẽ log và schema của chúng (có tính đến ràng buộc privacy), dSYM được upload tự động thế nào trong pipeline CI/CD, ngưỡng crash-free-rate nào sẽ dừng một phased rollout, và một tình huống debug mà thiếu breadcrumb sẽ khiến bạn không thể chẩn đoán một bug chỉ xảy ra ở production.
