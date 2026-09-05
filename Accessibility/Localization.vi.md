[English](./Localization.md) | [Tiếng Việt](./Localization.vi.md)

[← Accessibility và Localization](./README.vi.md)

# Localization và Internationalization

## Ý chính

Localization không phải là dịch string sau khi UI đã build xong — layout, format, và số nhiều phải được thiết kế cho text có độ dài, hướng, và ngữ pháp thay đổi ngay từ đầu, nếu không mỗi locale được dịch sẽ trở thành một bug report.

## Những điều cần nắm

- String Catalog (`.xcstrings`) — thay thế `Localizable.strings` + `.stringsdict`; Xcode tự động extract string literal bọc trong `String(localized:)` hoặc `Text` của SwiftUI, theo dõi trạng thái dịch theo từng locale
- Số nhiều (pluralization) — `String(localized:, options: .init(...))` / quy tắc kiểu stringsdict; "1 item" vs "5 items" không chỉ là `%d` như tiếng Anh — một số locale có hơn hai category số nhiều
- `FormatStyle` — format nhận biết locale cho date, number, currency, measurement (`.formatted(.currency(code:))`, `.formatted(date:time:)`) thay vì tự dựng string tay, thứ âm thầm gãy với RTL hoặc dấu thập phân/phân nhóm khác nhau
- Layout phải-sang-trái (RTL) — environment value `layoutDirection`, constraint và stack alignment dùng leading/trailing (không phải left/right), SF Symbols mirrored vs không mirrored
- Độ dài text mở rộng — string tiếng Đức/Phần Lan có thể dài hơn tiếng Anh 30-50%; nút có chiều rộng cố định và label bị cắt là lỗi localization phổ biến nhất
- Identifier độc lập với locale — không bao giờ dùng một string đã hiển thị, đã localize làm key tra cứu hoặc giá trị lưu trữ (ví dụ đừng switch theo tên ngày đã dịch)
- Test — pseudo-localization và scheme "Double-Length Pseudolanguage" / RTL pseudolanguage trong scheme editor của Xcode để bắt lỗi layout và text-key mà không cần chờ bản dịch thật

## Ví dụ

```swift
Text("cart_item_count", comment: "Số lượng item trong giỏ hàng")
    // resolve qua String Catalog, tự chọn đúng dạng số nhiều theo locale

let price = 12.5
Text(price, format: .currency(code: currentLocale.currency?.identifier ?? "USD"))
```

## Câu hỏi luyện tập

- Tại sao `String(format: "%d items", count)` sai khi ship cho locale Ả Rập hoặc Nga?
- Layout UIKit dựng bằng constraint `.left`/`.right` gãy chỗ nào khi app chạy ở tiếng Ả Rập?
- Tại sao một feature flag hoặc analytics event không bao giờ nên dùng string đã localize làm key?

## Góc nhìn Senior

Câu hỏi localization kiểm tra xem "ship tiếng Anh trước, dịch sau" có bao giờ là một giả định an toàn ở team này không. Nó gần như không bao giờ an toàn — text expansion, RTL mirroring, và quy tắc số nhiều là quyết định về layout và data model có tính cấu trúc, không phải việc đổi string ở phút chót. Câu trả lời senior nêu được một case cụ thể mà việc retrofit localization đòi hỏi công sức kỹ thuật thật sự (viết lại UI chiều rộng cố định, thay date string tự dựng) thay vì coi đó là vấn đề của team dịch thuật.

## Bài tập

Một màn hình checkout hiển thị: "Bạn đã tiết kiệm $12.50 (20%) — 3 sản phẩm trong giỏ, miễn phí ship cho đơn trên $50." Viết lại bằng key String Catalog và `FormatStyle` sao cho đúng với một locale phải-sang-trái, không phải tiếng Anh, có currency, dấu thập phân, và quy tắc số nhiều khác — và giải thích giả định layout UI nào (chiều rộng cố định, constraint `.left`/`.right`, mirroring icon) cần thay đổi để hỗ trợ nó.
