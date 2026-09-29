[English](./Localization.md) | [Tiếng Việt](./Localization.vi.md)

[← Accessibility và Localization](./README.vi.md)

# Localization và Internationalization

## Ý chính

Localization không phải là dịch string sau khi UI đã build xong — layout, format, và số nhiều phải được thiết kế cho text có độ dài, hướng, và ngữ pháp thay đổi ngay từ đầu, nếu không mỗi locale được dịch sẽ trở thành một bug report.

## Những điều cần nắm

- String Catalog (`.xcstrings`, từ Xcode 15) — thay thế `Localizable.strings` + `.stringsdict` bằng một file duy nhất; mỗi lần build, Xcode tự động extract các string literal dùng làm key localize (trong `Text` của SwiftUI, `String(localized:)`, `LocalizedStringResource`, `NSLocalizedString`…) vào catalog, và theo dõi trạng thái dịch của từng key theo từng locale
- Số nhiều (pluralization) — viết string có interpolation số, ví dụ `String(localized: "\(count) items")`, rồi chọn "Vary by Plural" cho key đó trong String Catalog (trước đây là `.stringsdict`); runtime tự chọn dạng đúng theo số và locale. "1 item" vs "5 items" không chỉ là `%d` như tiếng Anh — theo quy tắc CLDR, một số ngôn ngữ có tới sáu category số nhiều (`zero`, `one`, `two`, `few`, `many`, `other`)
- `FormatStyle` — format nhận biết locale cho date, number, currency, measurement (`.formatted(.currency(code:))`, `.formatted(date:time:)`) thay vì tự dựng string tay, thứ âm thầm gãy với RTL hoặc dấu thập phân/phân nhóm khác nhau
- Layout phải-sang-trái (RTL) — environment value `layoutDirection`, constraint và stack alignment dùng leading/trailing (không phải left/right), SF Symbols mirrored vs không mirrored
- Độ dài text mở rộng — string tiếng Đức/Phần Lan thường dài hơn tiếng Anh khoảng 30–40%, còn string ngắn (label một hai chữ) có thể dài gấp đôi hoặc hơn; nút có chiều rộng cố định và label bị cắt là lỗi localization phổ biến nhất
- Identifier độc lập với locale — không bao giờ dùng một string đã hiển thị, đã localize làm key tra cứu hoặc giá trị lưu trữ (ví dụ đừng switch theo tên ngày đã dịch)
- Test — pseudo-localization: trong scheme editor của Xcode (Run → Options → App Language) chọn "Double-Length Pseudolanguage" (mọi string bị nhân đôi độ dài) hoặc "Right-to-Left Pseudolanguage" (layout bị lật như tiếng Ả Rập) để bắt lỗi layout, text bị cắt và string quên localize mà không cần chờ bản dịch thật

## Ví dụ

```swift
// Key có interpolation số → trong String Catalog là "%lld items in cart", chọn "Vary by Plural".
// Runtime tự chọn đúng dạng số nhiều theo `count` và locale.
Text("\(count) items in cart", comment: "Số lượng item trong giỏ hàng")

// Số tiền và mã tiền tệ đi cùng nhau từ dữ liệu (server/StoreKit).
struct Price {
    let amount: Decimal
    let currencyCode: String   // ví dụ "USD" — thuộc về dữ liệu, không phải thiết bị
}

let price = Price(amount: 12.5, currencyCode: "USD")
// Locale của user chỉ quyết định CÁCH hiển thị ("$12.50", "12,50 $"…), không quyết định loại tiền.
Text(price.amount, format: .currency(code: price.currencyCode))
```

## Câu hỏi luyện tập

- Tại sao `String(format: "%d items", count)` sai khi ship cho locale Ả Rập hoặc Nga?
- Layout UIKit dựng bằng constraint `.left`/`.right` gãy chỗ nào khi app chạy ở tiếng Ả Rập?
- Tại sao một feature flag hoặc analytics event không bao giờ nên dùng string đã localize làm key?

## Góc nhìn Senior

Câu hỏi localization kiểm tra xem "ship tiếng Anh trước, dịch sau" có bao giờ là một giả định an toàn ở team này không. Nó gần như không bao giờ an toàn — text expansion, RTL mirroring, và quy tắc số nhiều là quyết định về layout và data model có tính cấu trúc, không phải việc đổi string ở phút chót. Câu trả lời senior nêu được một case cụ thể mà việc retrofit localization đòi hỏi công sức kỹ thuật thật sự (viết lại UI chiều rộng cố định, thay date string tự dựng) thay vì coi đó là vấn đề của team dịch thuật.

## Đáp án câu hỏi luyện tập

### Tại sao `String(format: "%d items", count)` sai khi ship cho locale Ả Rập hoặc Nga?

Vì nó giả định ngữ pháp tiếng Anh chỉ có một dạng "items" cho mọi số, trong khi tiếng Nga có ba dạng số nhiều và tiếng Ả Rập có tới sáu.

Tiếng Anh chỉ phân biệt "one" và "other". Theo quy tắc CLDR mà Apple dùng, với số nguyên tiếng Nga có `one` (1, 21, 31… trừ 11), `few` (2–4, 22–24… trừ 12–14), `many` (0, 5–20, 25–30…), cộng thêm `other` cho số thập phân; còn tiếng Ả Rập có `zero`, `one`, `two`, `few`, `many`, `other`. Chuỗi `"%d items"` có ba lỗi chồng lên nhau:

- Chữ "items" hard-code tiếng Anh, không đi qua bản dịch.
- Một format duy nhất không thể chọn đúng dạng từ theo số.
- `String(format:)` không truyền locale (khác với `String(format:locale:)`) nên số không được format theo locale của user (ví dụ chữ số Ả Rập-Ấn, dấu phân nhóm).

Cách đúng là để String Catalog chọn dạng số nhiều:

```swift
let label = String(localized: "\(count) items in cart",
                   comment: "Số item trong giỏ hàng")
// Trong .xcstrings: key "%lld items in cart" → Vary by Plural
```

Người dịch điền từng category mà ngôn ngữ đó cần; runtime chọn đúng dạng theo `count` và locale.

Trade-off: plural variation chỉ giải quyết số đếm. Giới tính, cách ngữ pháp (case) hay số nhiều trong câu có hai biến số vẫn cần người dịch xem ngữ cảnh — hãy viết `comment` rõ ràng cho mỗi key.

### Layout UIKit dựng bằng constraint `.left`/`.right` gãy chỗ nào khi app chạy ở tiếng Ả Rập?

Constraint `.left`/`.right` là hướng vật lý cố định nên không được lật khi layout là phải-sang-trái, và toàn bộ màn hình vẫn đọc theo kiểu tiếng Anh dù text đã là tiếng Ả Rập.

Với RTL, user đọc từ phải sang trái nên mắt tìm tiêu đề, avatar, nút back ở bên phải. `.leading`/`.trailing` được UIKit tự lật theo `effectiveUserInterfaceLayoutDirection`; `.left`/`.right` thì không. Kết quả thường thấy:

- Avatar vẫn nằm bên trái, text căn phải, bố cục trông ngược và lộn xộn.
- `NSTextAlignment.left` thay vì `.natural` làm text Ả Rập bị căn sai.
- `UIEdgeInsets` với `left`/`right` thay vì `NSDirectionalEdgeInsets`.
- Chevron, mũi tên "tiếp theo" không lật, trỏ sai hướng; ảnh custom cần `imageFlippedForRightToLeftLayoutDirection()`.
- Animation trượt dùng `translationX` dương giả định "đi sang phải là tiến tới".

Cách sửa: đổi hết sang leading/trailing, dùng directional insets, và test bằng RTL pseudolanguage trong scheme.

Trade-off: không phải thứ gì cũng nên lật. Số điện thoại, đồng hồ, logo, icon vật thể thật và những view có `semanticContentAttribute = .forceLeftToRight` có chủ đích (ví dụ bàn phím số) phải giữ nguyên hướng.

### Tại sao một feature flag hoặc analytics event không bao giờ nên dùng string đã localize làm key?

Vì string đã localize thay đổi theo ngôn ngữ của user và theo mỗi lần sửa bản dịch, nên cùng một thứ lại có nhiều key khác nhau và dữ liệu bị vỡ.

Key cần ổn định và giống nhau cho mọi user. Một string hiển thị thì không:

- User tiếng Việt gửi event `"Thanh toán"`, user tiếng Anh gửi `"Checkout"` — dashboard đếm thành hai event, funnel theo locale sai hoàn toàn.
- Người dịch sửa lỗi chính tả, key đổi, dữ liệu lịch sử đứt đoạn mà không ai biết.
- Flag tra theo tên hiển thị sẽ không khớp ở locale khác, nên feature âm thầm tắt (hoặc bật) sai.
- So sánh string phụ thuộc locale, ví dụ chữ "i" trong tiếng Thổ Nhĩ Kỳ, gây lỗi khi lowercase.

Cách đúng là dùng identifier ổn định không bao giờ hiển thị cho user, và chỉ localize ở lớp trình bày:

```swift
enum CheckoutStep: String { case cart, payment, review }
Analytics.log(event: .stepViewed(step: .payment))   // key cố định
Text("checkout.step.payment")                        // chỉ để hiển thị
```

Trade-off: nếu cần biết user đang dùng ngôn ngữ nào, gửi `Locale.current.identifier` như một property riêng, không trộn vào tên event.

## Bẫy phỏng vấn

### "`Text(product.name)` và `Text("welcome_title")` có cùng được localize không?"

**Dễ trả lời sai:** Có, `Text` luôn tra String Catalog nên đưa gì vào cũng được dịch.

**Nên trả lời:** Chỉ string literal mới được hiểu là `LocalizedStringKey` và được tra bản dịch. Khi truyền một biến kiểu `String`, SwiftUI dùng initializer `Text<S: StringProtocol>` và hiển thị nguyên văn, không dịch. Đây là hành vi đúng cho dữ liệu từ server (tên sản phẩm), nhưng là bug nếu bạn truyền một key qua biến. Muốn truyền key qua nhiều lớp thì dùng `LocalizedStringResource` hoặc `LocalizedStringKey`, không dùng `String`.

### "Format giá theo `Locale.current` là xong phần currency chưa?"

**Dễ trả lời sai:** Rồi, `.currency(code: Locale.current.currency?.identifier ?? "USD")` sẽ tự hiển thị đúng tiền cho mỗi user.

**Nên trả lời:** `FormatStyle` chỉ đổi cách hiển thị (ký hiệu, dấu thập phân, vị trí ký hiệu), không đổi tỷ giá. Lấy 12.5 rồi format bằng currency của locale thiết bị sẽ biến 12.5 USD thành "12,50 €" với user ở Đức, hay chỉ còn khoảng 12–13 ₫ với user ở Việt Nam — một con số sai. Currency là dữ liệu nghiệp vụ, phải đi kèm số tiền từ server hoặc từ StoreKit (`product.displayPrice` đã được format sẵn theo storefront của user); còn locale chỉ quyết định cách format. Vì vậy ví dụ trong file dùng `.currency(code: price.currencyCode)`, với mã tiền tệ lấy từ chính dữ liệu giá.

### "String Catalog yêu cầu deployment target iOS 17 đúng không?"

**Dễ trả lời sai:** Đúng, `.xcstrings` là tính năng mới nên chỉ chạy trên iOS 17+, app còn hỗ trợ iOS 15 phải giữ `Localizable.strings`.

**Nên trả lời:** String Catalog là tính năng của Xcode (từ Xcode 15), không phải của runtime. Lúc build, Xcode compile `.xcstrings` thành `.strings` / `.stringsdict` trong bundle, nên app vẫn chạy được trên các iOS cũ. Lợi ích thật là tự extract key từ code, gộp plural và device variation vào một file, và theo dõi trạng thái dịch (new, stale, needs review) cho từng locale.

## Bài tập

Một màn hình checkout hiển thị: "Bạn đã tiết kiệm $12.50 (20%) — 3 sản phẩm trong giỏ, miễn phí ship cho đơn trên $50." Viết lại bằng key String Catalog và `FormatStyle` sao cho đúng với một locale phải-sang-trái, không phải tiếng Anh, có currency, dấu thập phân, và quy tắc số nhiều khác — và giải thích giả định layout UI nào (chiều rộng cố định, constraint `.left`/`.right`, mirroring icon) cần thay đổi để hỗ trợ nó.
