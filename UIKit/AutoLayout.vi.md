[English](./AutoLayout.md) | [Tiếng Việt](./AutoLayout.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# Auto Layout

## Ý chính

Auto Layout là một hệ constraint. Layout ổn định đến từ priority rõ ràng, hiểu `intrinsicContentSize`, và tránh constraint mơ hồ hoặc xung đột.

## Cần ôn

- Constraint priority: mỗi constraint có priority từ 1 đến 1000. 1000 (`.required`) là bắt buộc, Auto Layout phải thỏa mãn, nếu không được thì báo lỗi unsatisfiable và tự bỏ một constraint. Dưới 1000 là tùy chọn: Auto Layout cố gắng thỏa mãn, còn khi có xung đột thì constraint priority thấp hơn nhường.
- `contentHuggingPriority` và `contentCompressionResistancePriority`: hai priority ngầm mà mỗi view có nội dung (label, button, image view) dùng để bảo vệ `intrinsicContentSize` của nó, một cái chống bị giãn to, một cái chống bị ép nhỏ (xem bẫy phỏng vấn bên dưới).
- Điểm mạnh và giới hạn của `UIStackView`
- Cách debug unsatisfiable constraints: đọc log "Unable to simultaneously satisfy constraints" trong console (log liệt kê các constraint xung đột và constraint bị hệ thống bỏ đi), đặt `identifier` cho constraint để log dễ đọc, thêm symbolic breakpoint `UIViewAlertForUnsatisfiableConstraints` để dừng đúng lúc lỗi xảy ra, và dùng View Debugger của Xcode để xem constraint của từng view. Với layout mơ hồ (ambiguous) thì không có log lỗi, có thể kiểm tra bằng `view.hasAmbiguousLayout` khi debug.

## Câu hỏi thực hành

- Vì sao label bị compress ngoài ý muốn?
- Khi nào nên dùng `UIStackView`, khi nào không?

## Câu hỏi luyện tập

- Tại sao một label bị nén lại ngoài ý muốn?
- Khi nào nên dùng UIStackView và khi nào không?

## Góc nhìn senior

Phần lớn lỗi layout không phải vì “Auto Layout bị hỏng”. Chúng là vấn đề về ownership và định nghĩa constraint. Câu trả lời senior nên nối triệu chứng với quy tắc đang xung đột.

## Đáp án câu hỏi luyện tập

### Tại sao một label bị nén lại ngoài ý muốn?

Label bị nén vì trong hệ constraint có một ràng buộc khác có priority cao hơn compression resistance của label, nên Auto Layout chọn hy sinh label. Mặc định label có `contentCompressionResistancePriority` là 750 (`.defaultHigh`), còn constraint bạn tạo ra mặc định là 1000 (`.required`). Khi không đủ chỗ, constraint 1000 luôn thắng và label bị cắt.

Các nguyên nhân hay gặp:

- Hai label đứng cạnh nhau có cùng compression resistance. Layout bị mơ hồ và Auto Layout tự chọn một bên để nén, có khi lại chọn đúng cái tên người dùng mà bạn muốn giữ.
- Một view bên cạnh (button, icon) có width cố định với priority 1000, hoặc stack view dùng `.fillEqually` chia đều không gian.
- Label trong cell nhiều dòng nhưng `numberOfLines` vẫn là 1, hoặc cell không self-sizing nên chiều cao bị khóa.

Cách sửa là nói rõ cho Auto Layout biết thứ tự ưu tiên. Với profile header trong bài tập:

```swift
actionButton.setContentCompressionResistancePriority(.required, for: .horizontal)
actionButton.setContentHuggingPriority(.required, for: .horizontal)
nameLabel.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
nameLabel.lineBreakMode = .byTruncatingTail
```

Button giữ nguyên kích thước và vùng chạm, tên dài sẽ truncate có dấu "...". Trade-off: đừng sửa bằng cách đặt width cố định cho label, vì sẽ vỡ với Dynamic Type và ngôn ngữ khác.

### Khi nào nên dùng UIStackView và khi nào không?

Nên dùng `UIStackView` khi các view xếp thành một hàng hoặc một cột, và bạn muốn hệ thống tự lo khoảng cách, căn lề và việc ẩn hiện. Điểm mạnh lớn nhất: khi đặt `isHidden = true` cho một arranged subview, stack view tự bỏ view đó khỏi layout và dồn các view còn lại, không cần sửa constraint. Nó cũng hợp với Dynamic Type, ví dụ đổi `axis` từ ngang sang dọc khi chữ quá to.

Không nên dùng khi:

- Layout không tuyến tính: view chồng lên nhau, căn theo baseline của một view ở hàng khác, hoặc cần quan hệ giữa hai view không cùng stack. Lồng stack trong stack nhiều tầng để "ép" layout này sẽ khó đọc hơn viết constraint trực tiếp.
- Cell trong list rất dài mà dùng nhiều stack lồng nhau. Mỗi stack sinh thêm constraint nội bộ, cộng lại sẽ tốn thời gian layout khi scroll nhanh.
- Cần kiểm soát chi tiết priority của từng khoảng cách.

Một ghi chú về version: trước iOS 14, stack view không vẽ gì nên `backgroundColor` không có tác dụng. Từ iOS 14 thì đã hoạt động. Trade-off chung: stack view giúp code ngắn và dễ sửa, nhưng khi gặp lỗi layout bạn phải hiểu cả những constraint mà nó tự tạo ra.

## Bẫy phỏng vấn

### "Content hugging và compression resistance khác nhau thế nào?"

**Dễ trả lời sai:** Hai cái gần như giống nhau, priority càng cao thì view càng "giữ" kích thước của nó.

**Nên trả lời:** Hai priority tác động theo hai chiều ngược nhau. Hugging chống lại việc bị kéo **to hơn** intrinsic size, nên view có hugging cao sẽ không giãn ra lấp chỗ trống. Compression resistance chống lại việc bị ép **nhỏ hơn** intrinsic size, nên view có resistance cao sẽ không bị truncate. Trong hàng gồm label và button, bạn thường muốn label có hugging thấp (được giãn) và resistance thấp hơn button (bị cắt trước).

### "Tạo view bằng code, add constraint mà layout vẫn lỗi, vì sao?"

**Dễ trả lời sai:** Do constraint bị sai số, cần gọi `layoutIfNeeded()` hoặc thêm constraint nữa cho chắc.

**Nên trả lời:** Nguyên nhân kinh điển là quên `translatesAutoresizingMaskIntoConstraints = false`. Với view tạo bằng code, giá trị này mặc định là `true`, nên UIKit tự sinh `NSAutoresizingMaskLayoutConstraint` từ frame, và chúng xung đột với constraint của bạn. Log unsatisfiable constraints sẽ có dòng `NSAutoresizingMaskLayoutConstraint`, đó là dấu hiệu nhận biết. `NSLayoutConstraint.activate` không tự tắt cờ này, còn view từ Interface Builder thì đã tắt sẵn.

### "Có thể đổi priority của một constraint lúc runtime để bật tắt layout không?"

**Dễ trả lời sai:** Được, cứ đổi `priority` từ 1000 xuống 250 và ngược lại là xong.

**Nên trả lời:** Đổi priority giữa các giá trị tùy chọn (dưới 1000) thì được. Nhưng đổi từ `.required` sang không-required, hoặc ngược lại, trên một constraint đang active sẽ gây exception. Hãy dùng 999 thay cho 1000 nếu cần đổi, hoặc giữ hai constraint và bật tắt bằng `isActive` (deactivate cái cũ trước rồi mới activate cái mới để tránh xung đột tạm thời).

## Bài tập

Xây một profile header gồm avatar, name, subtitle, và action button. Giải thích cách đặt priority để tên dài vẫn truncate đúng còn button vẫn đủ vùng chạm.
