[English](./Refactoring.md) | [Tiếng Việt](./Refactoring.vi.md)

[← Chủ đề Senior](./README.vi.md)

# Chiến lược Refactoring

## Khi nào nên Refactor

- Trước khi thêm tính năng vào vùng sẽ khó thay đổi hơn
- Khi cùng một bug xuất hiện lặp lại trong cùng module
- Khi onboarding engineer mới liên tục cần giải thích cùng một vùng khó hiểu
- Khi vùng code chưa có test nào nhưng sắp phải sửa — lúc này refactor nhỏ để tạo seam (inject dependency) và thêm characterization test là bước chuẩn bị, không phải refactor lớn

## Khi nào KHÔNG nên Refactor

- Ngay trước deadline release
- Khi code đang chạy ổn và không có kế hoạch sửa gì ở vùng đó — refactor lúc này chỉ thêm rủi ro mà không đem lại lợi ích
- Như điều kiện tiên quyết cho tất cả công việc khác ("không thể thêm tính năng cho đến khi refactor tất cả")

## Các cách tiếp cận

- **Strangler Fig** — xây hệ thống mới song song với cũ, dần dần chuyển traffic, xóa code cũ khi xong
- **Extract and redirect** — tách logic vào module/class mới, chuyển hướng caller từng cái một
- **Characterization tests** — viết test để ghi lại behavior hiện tại trước khi thay đổi

## Câu hỏi thực hành

- Khi nào refactor và khi nào để code như cũ?
- Bạn refactor legacy codebase mà không phá vỡ behavior hiện tại như thế nào?

## Câu hỏi luyện tập

- Khi nào nên refactor và khi nào nên để code như cũ?
- Bạn refactor một codebase legacy mà không làm gãy behavior hiện có như thế nào?

## Góc nhìn senior

Refactor mà không có test thì nguy hiểm. Bước đầu tiên gần như luôn là: thêm test cho behavior hiện tại, rồi mới thay đổi. Characterization test ghi lại behavior hiện tại — kể cả bug — để bạn biết khi nào có gì đó thay đổi.

## Đáp án câu hỏi luyện tập

### Khi nào nên refactor và khi nào nên để code như cũ?

Tôi refactor khi code xấu đang cản trở công việc sắp làm, và để yên khi code xấu nhưng ổn định và không ai cần chạm vào.

Code "xấu" tự nó chưa phải lý do. Lý do là chi phí thật: bug lặp lại trong cùng module, mỗi tính năng mới ở vùng đó tốn gấp đôi thời gian, hoặc engineer mới lần nào cũng phải hỏi về cùng một chỗ.

Nên refactor khi:

- Sắp thêm tính năng vào vùng đó — refactor vừa đủ để tính năng mới gọn gàng ("make the change easy, then make the easy change").
- Bug lặp lại do cấu trúc, ví dụ cùng một state bị lưu ở hai nơi và lệch nhau.

Nên để yên khi:

- Code chạy ổn, ít thay đổi, ít bug — refactor lúc này chỉ thêm rủi ro.
- Ngay trước release deadline.
- Không có test và cũng không có thời gian viết characterization test.

Tôi cũng tránh đề xuất kiểu "dừng feature hai tháng để refactor toàn bộ" — product khó đồng ý và rủi ro rất cao. Tốt hơn là refactor từng bước gắn với feature work, và trình bày lợi ích bằng con số cho stakeholder (số bug, thời gian làm tính năng).

Trade-off: nếu cứ hoãn mãi, nợ kỹ thuật sẽ tích tụ. Nên có một ngân sách cố định, ví dụ 10–20% capacity mỗi sprint, cho những vùng gây đau nhất.

### Bạn refactor một codebase legacy mà không làm gãy behavior hiện có như thế nào?

Cách an toàn là khóa behavior hiện tại bằng test trước, rồi thay đổi từng bước nhỏ, mỗi bước đều có thể ship và rollback được.

Quy trình tôi dùng, lấy ví dụ `MassiveViewController`:

1. **Characterization test** cho các behavior quan trọng nhất — tính tổng tiền, validate form, xử lý lỗi network. Test ghi lại những gì code đang làm, kể cả hành vi hơi sai, để biết ngay khi có gì thay đổi.
2. **Tạo seam:** đưa dependency như `URLSession`, `UserDefaults`, singleton vào qua init hoặc protocol, để test được mà chưa đổi logic.
3. **Extract and redirect:** tách một trách nhiệm (ví dụ validation) ra class mới, chuyển từng caller sang class mới, chạy test sau mỗi bước.
4. **Strangler Fig** cho thay đổi lớn hơn: xây implementation mới song song, bật bằng feature flag cho một phần người dùng, so sánh metrics, rồi mới xóa code cũ.
5. **PR refactor không trộn với thay đổi behavior**, để review dễ và nếu có regression thì biết ngay nguyên nhân.

Trade-off: characterization test cho UIKit code cũ có thể khó viết và chạy chậm. Khi đó ưu tiên test ở tầng logic ngay sau khi tách ra, kết hợp vài UI test hoặc snapshot test cho luồng chính. Đừng cố đạt coverage cao cho cả codebase trước khi bắt đầu — chỉ cần đủ cho vùng sắp chạm vào.

## Bẫy phỏng vấn

### "Code này tệ quá, sao không rewrite từ đầu?"

**Dễ trả lời sai:** "Tôi sẽ rewrite toàn bộ sang SwiftUI với kiến trúc mới cho sạch." Nghe có vẻ quyết đoán nhưng là red flag về judgment.

**Nên trả lời:** Big-bang rewrite hiếm khi thành công: bạn đánh mất hàng năm bug fix và edge case được mã hóa ngầm trong code cũ, feature phải dừng lâu, và trong thời gian đó hai codebase cùng tồn tại. Tôi chọn cách tăng dần với Strangler Fig, chuyển từng màn hình hoặc từng luồng. Rewrite chỉ hợp lý khi phạm vi nhỏ, có lý do cụ thể (như công nghệ cũ không còn được hỗ trợ), và có kế hoạch cắt chuyển rõ ràng.

### "Refactor tiện thể thêm luôn tính năng trong cùng PR được không?"

**Dễ trả lời sai:** "Được, đang mở file đó thì làm luôn cho nhanh." Khi có regression, không ai biết nó đến từ refactor hay từ tính năng mới.

**Nên trả lời:** Tách riêng. PR refactor không được đổi behavior, và test hiện có phải xanh mà không cần sửa test (trừ test gắn chặt vào cấu trúc nội bộ). PR tính năng đến sau, trên nền code đã sạch. Cách này làm review nhanh hơn, và khi cần revert thì revert được đúng phần có lỗi.

### "Trong lúc refactor bạn phát hiện một bug. Bạn sửa luôn chứ?"

**Dễ trả lời sai:** "Sửa luôn, đang refactor mà." Nghe hợp lý nhưng biến PR refactor thành PR đổi behavior.

**Nên trả lời:** Ghi nhận bug, để characterization test vẫn phản ánh hành vi hiện tại, rồi sửa trong một PR riêng có mô tả rõ. Lý do là có thể có phần khác của app, backend, hoặc chính người dùng đang phụ thuộc vào hành vi đó (Hyrum's law). Sửa riêng giúp đánh giá tác động, test đúng, và rollback được nếu cần.

## Bài tập

Chọn `MassiveViewController` trong project (hoặc tạo một cái giả với 400+ dòng). Viết characterization test cho ba behavior quan trọng nhất. Sau đó tách một trách nhiệm ra class mới bằng cách extract and redirect (chuyển từng caller sang class mới); nếu muốn luyện Strangler Fig, giữ cả đường cũ và mới song song sau một flag rồi mới xóa đường cũ. Xác minh tất cả test vẫn pass sau khi tách.
