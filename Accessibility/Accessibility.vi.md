[English](./Accessibility.md) | [Tiếng Việt](./Accessibility.vi.md)

[← Accessibility và Localization](./README.vi.md)

# Accessibility

## Ý chính

Accessibility không chỉ là một checkbox VoiceOver. Đó là việc giao diện có còn hoạt động hay không khi một kênh input/output nào đó bị suy giảm — thị giác, thính giác, khả năng vận động, hay khả năng đọc — và nó được test bằng cách thực sự dùng app theo cách đó, chứ không phải bằng cách đọc code.

## Những điều cần nắm

- VoiceOver cơ bản — `accessibilityLabel`, `accessibilityValue`, `accessibilityHint`, `accessibilityTraits`; label mô tả *cái gì*, value mô tả *trạng thái*, hint mô tả *chuyện gì xảy ra nếu kích hoạt*
- Gom nhóm và thứ tự đọc — `accessibilityElement(children:)`, thứ tự traversal tùy chỉnh (`accessibilitySortPriority` trong SwiftUI / mảng `accessibilityElements` trong UIKit) để VoiceOver đọc nội dung theo thứ tự hợp lý về nghĩa. Mặc định VoiceOver đi theo vị trí trên màn hình (trên xuống dưới, theo hướng đọc của ngôn ngữ) và cấu trúc view hierarchy, nên một layout nhiều cột hoặc có view chồng lên nhau dễ bị đọc lộn xộn. `accessibilityElement(children: .combine)` gộp nhiều view con thành một element để user chỉ cần vuốt một lần cho cả cell
- Dynamic Type — `.font(.body)` với text style hệ thống tự scale; point size cố định thì không; layout phải reflow, không chỉ bị cắt, ở các cỡ accessibility (tới `.accessibility5`)
- Custom action — `accessibilityActions` / `UIAccessibilityCustomAction` để expose các gesture chỉ có swipe (ví dụ "delete", "archive") cho user VoiceOver không thể swipe trên một cell
- Reduce Motion / Reduce Transparency — UIKit đọc `UIAccessibility.isReduceMotionEnabled` / `isReduceTransparencyEnabled`, SwiftUI đọc `@Environment(\.accessibilityReduceMotion)` / `@Environment(\.accessibilityReduceTransparency)`. Check trước khi chạy animation không cần thiết hoặc hiệu ứng parallax (thay bằng crossfade), và thay nền blur/trong suốt bằng nền đặc khi user bật Reduce Transparency
- Color contrast và "đừng chỉ dựa vào màu" — kết hợp trạng thái mã hóa bằng màu với icon hoặc text label cho user mù màu
- Quản lý focus — di chuyển VoiceOver focus sau khi một sheet hiện lên hoặc list được cập nhật, để focus không bị "mắc kẹt" âm thầm ở element cũ. Trong UIKit: `UIAccessibility.post(notification: .screenChanged, argument: view)` khi cả màn hình đổi (VoiceOver phát âm báo và nhảy tới `view`), `.layoutChanged` khi chỉ một phần layout đổi. Trong SwiftUI (iOS 15+): `@AccessibilityFocusState` kết hợp `.accessibilityFocused(_:)`
- Accessibility Inspector và công cụ Audit trong Xcode — check tự động (contrast, thiếu label, kích thước vùng tap) như một bước sàng lọc đầu, không thay thế cho việc test VoiceOver thủ công

## Ví dụ

```swift
// Button của SwiftUI đã có sẵn trait button — không cần (và không nên) thêm .isButton.
Button {
    toggleFavorite()
} label: {
    Image(systemName: isFavorite ? "heart.fill" : "heart")
}
.accessibilityLabel("Favorite")                 // cái gì: tên chức năng, không đổi theo trạng thái
.accessibilityValue(isFavorite ? "On" : "Off")  // trạng thái hiện tại

// Chỉ view tự dựng với onTapGesture mới phải tự thêm trait .isButton,
// vì hệ thống không biết nó bấm được. Tốt hơn nữa là đổi view này thành Button.
Image(systemName: "xmark")
    .onTapGesture { dismiss() }
    .accessibilityLabel("Close")
    .accessibilityAddTraits(.isButton)
```

## Câu hỏi luyện tập

- Tại sao `accessibilityLabel("Heart icon")` cho một nút favorite là một label tệ?
- Điều gì bị gãy trong một cell thiết kế chiều cao cố định khi user đặt cỡ Dynamic Type lớn nhất?
- Tại sao một biểu đồ tự vẽ (Canvas/Core Graphics) cần công sức accessibility tường minh mà một `List` gốc được miễn phí?

## Góc nhìn Senior

Câu hỏi accessibility phân biệt người đã thực sự bật VoiceOver lên dùng với người chỉ đọc về `accessibilityLabel`. Tín hiệu tốt là mô tả một lỗi cụ thể bạn tìm thấy khi test bằng VoiceOver hoặc ở Dynamic Type lớn nhất — một control không tới được, một label đọc sai, một layout bị cắt — và cách fix đã thay đổi cấu trúc view bên dưới, chứ không chỉ thêm label như một việc làm thêm sau cùng.

## Đáp án câu hỏi luyện tập

### Tại sao `accessibilityLabel("Heart icon")` cho một nút favorite là một label tệ?

Vì label đó mô tả hình dáng của icon chứ không mô tả nút làm gì, nên user VoiceOver nghe "Heart icon, button" mà vẫn không biết bấm vào sẽ ra sao.

Label trả lời câu hỏi "đây là cái gì" theo nghĩa chức năng. User sáng mắt hiểu trái tim nghĩa là "yêu thích" nhờ ngữ cảnh thị giác, còn user VoiceOver không có ngữ cảnh đó. "Heart icon" còn có ba lỗi phụ:

- Chữ "icon" thừa: VoiceOver đã đọc trait "button", người dùng không cần biết đó là hình ảnh.
- Nó không nói trạng thái. Đã favorite hay chưa là việc của `accessibilityValue`, như ví dụ trong file dùng `"On"` / `"Off"`.
- Nó mô tả hình ảnh chứ không mô tả chức năng, nên kể cả khi được dịch (literal trong `.accessibilityLabel("...")` của SwiftUI được coi là `LocalizedStringKey`), user ngôn ngữ khác vẫn chỉ nghe "biểu tượng trái tim". Còn nếu gán qua một biến `String` hoặc `accessibilityLabel = "Heart icon"` trong UIKit mà không qua `String(localized:)`, nó còn không được dịch.

Label tốt là ngắn, là danh từ/động từ chức năng, và không thay đổi theo trạng thái: `"Favorite"`. Nếu nhét trạng thái vào label (ví dụ `"Unfavorite"` khi đang bật), user sẽ bối rối vì cùng một nút lại đổi tên. Với nút bật/tắt, từ iOS 17 có thể thêm trait `.isToggle` để VoiceOver đọc đúng kiểu "switch", hoặc dùng luôn `Toggle`.

Trade-off: đôi khi label cần cụ thể hơn khi trong list có nhiều nút giống nhau, ví dụ "Favorite, Áo khoác xanh" — nhưng khi đó thường nên gộp cả cell bằng `accessibilityElement(children: .combine)` thay vì làm label dài ra.

### Điều gì bị gãy trong một cell thiết kế chiều cao cố định khi user đặt cỡ Dynamic Type lớn nhất?

Text bị cắt, bị chồng lên nhau hoặc bị rút gọn bằng "…", nên thông tin quan trọng như giá hay tên sản phẩm biến mất đúng với người cần chữ to nhất.

Ở cỡ `.accessibility5`, font body có thể to gấp khoảng ba lần cỡ mặc định. Một cell cao 60pt chỉ chứa được một phần dòng đầu. Các vấn đề thường gặp:

- Label bị clip hoặc truncate vì chiều cao/chiều rộng cố định.
- `HStack` icon + text bị ép, text chỉ còn vài chữ mỗi dòng.
- Icon không scale theo text nên nhìn lệch.

Cách sửa là để cell tự tính chiều cao (self-sizing), cho text `lineLimit(nil)`, và đổi layout khi ở cỡ accessibility: chuyển từ ngang sang dọc.

```swift
@Environment(\.dynamicTypeSize) private var size
@ScaledMetric private var iconSize = 24.0

var body: some View {
    let layout = size.isAccessibilitySize
        ? AnyLayout(VStackLayout(alignment: .leading))
        : AnyLayout(HStackLayout())
    layout {
        icon.frame(width: iconSize)
        details
    }
}
```

Trade-off: không phải UI nào cũng reflow được (tab bar, toolbar). Khi đó dùng Large Content Viewer, hoặc giới hạn bằng `.dynamicTypeSize(...DynamicTypeSize.accessibility2)` cho đúng phần tử đó — dùng dè dặt, không áp cho cả màn hình.

### Tại sao một biểu đồ tự vẽ (Canvas/Core Graphics) cần công sức accessibility tường minh mà một `List` gốc được miễn phí?

Vì Canvas hay Core Graphics chỉ vẽ ra pixel, không tạo ra element nào trong accessibility tree, nên với VoiceOver cả biểu đồ chỉ là một vùng trống hoặc một ảnh không tên.

`List` được dựng từ các view thật: mỗi row có text, có frame, có trait, và hệ thống tự biến chúng thành accessibility element theo thứ tự đọc hợp lý. Biểu đồ tự vẽ thì dữ liệu nằm trong code vẽ, VoiceOver không đọc được. Bạn phải tự cung cấp:

- Một tóm tắt tổng quan: label "Doanh thu 7 ngày", value "cao nhất thứ Sáu, 12 triệu".
- Element cho từng điểm dữ liệu để user vuốt qua lần lượt, qua `.accessibilityChildren { }` trong SwiftUI, hoặc `UIAccessibilityElement` với `accessibilityFrameInContainerSpace` trong UIKit.
- Tùy chọn `accessibilityChartDescriptor` (`AXChartDescriptor`, iOS 15+) để có Audio Graph — nghe biểu đồ bằng cao độ âm thanh.

Trade-off: một chart có 365 điểm mà mỗi điểm là một element thì user phải vuốt 365 lần. Nên gộp theo tuần/tháng hoặc chỉ expose tóm tắt + Audio Graph. Nếu được, dùng Swift Charts: nó tự sinh element và chart descriptor mặc định, tốn ít công hơn nhiều so với Canvas.

## Bẫy phỏng vấn

### "Nút này cần thêm `.accessibilityAddTraits(.isButton)` không?"

**Dễ trả lời sai:** Có, luôn thêm trait `.isButton` cho mọi nút để VoiceOver biết đó là nút.

**Nên trả lời:** `Button` của SwiftUI và `UIButton` đã có sẵn trait button, thêm lần nữa là thừa (vô hại nhưng cho thấy không hiểu mặc định của hệ thống). Trait `.isButton` chỉ cần cho view tự dựng bằng `onTapGesture` (như `Image(systemName: "xmark")` + `onTapGesture` trong ví dụ của file), và câu trả lời tốt hơn là đổi view đó thành `Button` để có luôn hành vi kích hoạt, focus bàn phím và Voice Control. Cái đáng thêm cho nút favorite là trạng thái: `.accessibilityValue` hoặc `.isToggle` (iOS 17+).

### "Accessibility Audit trong Xcode pass hết rồi, app đã accessible chưa?"

**Dễ trả lời sai:** Rồi, Accessibility Inspector và `performAccessibilityAudit()` trong XCUITest (iOS 17+) không báo lỗi nghĩa là đạt chuẩn.

**Nên trả lời:** Audit chỉ bắt được lỗi máy đo được: thiếu label, contrast thấp, vùng tap nhỏ, text bị clip. Nó không biết label "Button 3" có nghĩa hay không, thứ tự đọc có hợp lý không, focus có bị kẹt sau khi mở sheet không, hay flow nào đó có làm được bằng Switch Control không. Audit là bước sàng lọc trong CI; vẫn phải tự bật VoiceOver và Dynamic Type lớn nhất để đi qua các flow chính.

### "Khi Reduce Motion bật thì làm gì với animation?"

**Dễ trả lời sai:** Tắt hết animation, cho mọi thứ nhảy thẳng sang trạng thái mới.

**Nên trả lời:** Reduce Motion nhắm vào chuyển động gây chóng mặt: zoom, parallax, trượt lớn, xoay. Nên thay chúng bằng hiệu ứng nhẹ như crossfade, chứ không bỏ luôn phản hồi thị giác, vì user vẫn cần biết trạng thái đã đổi. Trong SwiftUI đọc `@Environment(\.accessibilityReduceMotion)` rồi chọn `.opacity` thay cho `.move`/`.scale`.

## Bài tập

Lấy một component card tùy chỉnh hiển thị ảnh sản phẩm, tên, giá, giá gốc gạch ngang, và badge "giảm 20%" là một ribbon màu ở góc. Nêu rõ: thứ tự đọc VoiceOver và label/value gộp lại, giảm giá được truyền tải ra sao mà không chỉ dựa vào màu của ribbon, cái gì thay đổi ở cỡ Dynamic Type lớn nhất, và một custom action bạn sẽ thêm cho user VoiceOver tương đương với gesture vuốt mà user sáng mắt có.
