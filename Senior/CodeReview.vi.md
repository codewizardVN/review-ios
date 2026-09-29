[English](./CodeReview.md) | [Tiếng Việt](./CodeReview.vi.md)

[← Chủ đề Senior](./README.vi.md)

# Tư duy Code Review

## Cần nhìn vào gì

- **Correctness** — code có làm đúng ý định không? Edge case được xử lý chưa?
- **Readability** — engineer tiếp theo có hiểu được mà không cần giải thích không?
- **Safety** — memory, threading, error handling, force unwrap
- **Testability** — code mới có thể test không? Có phá vỡ test hiện tại không?
- **Architecture fit** — có tuân theo pattern đã thiết lập không, hay giới thiệu pattern mới vô lý?

## Cách đưa feedback

- Cụ thể — chỉ rõ dòng và giải thích lý do
- Phân biệt blocking với suggestion — dùng nhãn `[nit]`, `[suggestion]`, `[blocking]`
- Hỏi trước khi giả định — "Ý định ở đây là gì?" mở ra đối thoại
- Ghi nhận code tốt — không chỉ vấn đề

## Câu hỏi thực hành

- Bạn review một PR lớn như thế nào?
- Bạn xử lý bất đồng về approach như thế nào?

## Câu hỏi luyện tập

- Bạn review một PR lớn như thế nào?
- Bạn xử lý bất đồng về cách tiếp cận ra sao?

## Góc nhìn senior

Code review là cơ hội dạy học và cổng chất lượng — không phải bài tập kiểm soát. Mục tiêu là codebase tốt hơn và team mạnh hơn, không phải chứng minh reviewer thông minh hơn.

## Đáp án câu hỏi luyện tập

### Bạn review một PR lớn như thế nào?

Trước hết tôi hỏi PR này có thật sự cần lớn như vậy không; nếu được, tôi đề nghị tách thành nhiều PR nhỏ theo từng bước logic, vì chất lượng review giảm rõ rệt khi PR lên tới hàng nghìn dòng.

Nếu không tách được (ví dụ một migration đã làm xong), tôi review theo thứ tự:

1. Đọc mô tả PR, ticket, design doc để hiểu ý định và phạm vi.
2. Nhìn cấu trúc tổng thể trước: file nào mới, public API hay protocol nào thay đổi, dependency nào được thêm vào.
3. Đi sâu vào vùng rủi ro cao: concurrency, persistence và migration, thanh toán, code chạy lúc app launch, thay đổi API contract.
4. Kiểm tra test: có test cho hành vi mới và edge case không.
5. Để phần rename, format, refactor cơ học cho cuối cùng và lướt nhanh.

Với PR rất lớn, tôi thường xin tác giả walkthrough 15 phút, hoặc review theo từng commit nếu commit được tách gọn. Comment được gắn nhãn `[blocking]`, `[suggestion]`, `[nit]` để tác giả biết đâu là bắt buộc phải sửa.

Trade-off: đòi tách PR cũng tốn thời gian của tác giả. Nếu deadline gấp, có thể chấp nhận review tập trung vào vùng rủi ro và tạo ticket follow-up cho phần còn lại. Điều không nên làm là approve "LGTM" cho một PR khổng lồ mà không thật sự đọc.

### Bạn xử lý bất đồng về cách tiếp cận ra sao?

Tôi tách bất đồng làm hai loại: vấn đề có tiêu chí khách quan (correctness, crash, security, vi phạm quy ước team đã thống nhất) thì giữ `[blocking]`; vấn đề thuộc về sở thích thì để tác giả quyết.

Cách làm cụ thể:

- **Hỏi ý định trước:** "Lý do chọn cách này là gì?" — nhiều khi tác giả có context mà reviewer không có.
- **Nói bằng hệ quả, không bằng cảm tính.** Ví dụ với `UserProfileViewModel` gọi `URLSession.shared` trong `init`: "Network chạy ngay trong init nên view model không test được bằng mock, và mỗi lần view được tạo lại có thể gửi thêm request."
- **Đưa ra phương án thay thế:** inject một protocol `ProfileService` qua init và gọi load trong `.task`.
- **Đổi kênh khi cần:** sau 2–3 lượt comment chưa thống nhất thì chuyển sang nói chuyện trực tiếp hoặc call ngắn; thread dài dễ biến thành tranh cãi.
- **Nhờ người thứ ba nếu bế tắc:** tech lead, owner của module, hoặc guideline của team; nếu có quy ước mới thì ghi lại để lần sau không phải tranh luận lại.

Trade-off: không phải bất đồng nào cũng đáng chặn PR. Nếu cách của tác giả chấp nhận được và dễ sửa về sau, tôi approve kèm suggestion — giữ tốc độ và niềm tin trong team quan trọng hơn việc thắng một cuộc tranh luận.

## Bẫy phỏng vấn

### "Bạn thường để lại bao nhiêu comment? Bạn bắt được những lỗi gì?"

**Dễ trả lời sai:** Tự hào vì review rất kỹ, để lại hàng chục comment về khoảng trắng, thứ tự import, cách đặt dấu ngoặc. Điều này cho thấy bạn dùng thời gian của con người cho việc máy làm được.

**Nên trả lời:** Style và format nên được tự động hóa bằng SwiftLint hoặc SwiftFormat trên CI để không ai phải comment về chúng. Reviewer tập trung vào correctness, thiết kế, rủi ro và khả năng bảo trì. Số lượng comment không phải thước đo chất lượng review; một comment `[blocking]` đúng chỗ giá trị hơn 30 nit.

### "CI đã xanh, test pass hết. Còn cần đọc kỹ không?"

**Dễ trả lời sai:** "CI pass là đủ, tôi chỉ lướt qua." Test pass chỉ chứng minh những test hiện có pass, không chứng minh code đúng.

**Nên trả lời:** CI không bắt được lỗi thiết kế, race condition, edge case chưa có test, thay đổi ảnh hưởng tới privacy manifest hay data collection, hoặc migration dữ liệu thiếu. Reviewer cũng cần hỏi "test nào còn thiếu?" chứ không chỉ "test có pass không?". CI là lưới an toàn cơ bản, còn review là nơi bắt những gì máy không hiểu.

### Phát hiện vấn đề kiến trúc lớn ở một PR đã gần xong

**Dễ trả lời sai:** Chặn PR và yêu cầu viết lại toàn bộ, hoặc ngược lại, im lặng approve để tránh va chạm.

**Nên trả lời:** Đánh giá tác động trước: nếu vấn đề gây bug hoặc khóa chặt hướng đi khó đảo ngược thì chặn và cùng tác giả tìm cách sửa gọn nhất; nếu chỉ chưa tối ưu thì merge kèm ticket follow-up. Quan trọng hơn là sửa nguyên nhân gốc: task lớn cần design review hoặc draft PR từ sớm, để bất đồng kiến trúc xuất hiện trước khi viết hàng nghìn dòng code.

## Bài tập

Review một PR giới thiệu `UserProfileViewModel` với lời gọi `URLSession.shared` bên trong `init`. Viết ba comment: một `[blocking]` cho vấn đề kiến trúc, một `[suggestion]` cho đặt tên, và một lời thừa nhận điều gì đó được làm tốt. Sau đó giải thích cách bạn xử lý phản đối từ tác giả không đồng ý với comment blocking.
