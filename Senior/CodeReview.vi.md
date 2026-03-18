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

## Góc nhìn senior

Code review là cơ hội dạy học và cổng chất lượng — không phải bài tập kiểm soát. Mục tiêu là codebase tốt hơn và team mạnh hơn, không phải chứng minh reviewer thông minh hơn.

## Bài tập

Review một PR giới thiệu `UserProfileViewModel` với lời gọi `URLSession.shared` bên trong `init`. Viết ba comment: một `[blocking]` cho vấn đề kiến trúc, một `[suggestion]` cho đặt tên, và một lời thừa nhận điều gì đó được làm tốt. Sau đó giải thích cách bạn xử lý phản đối từ tác giả không đồng ý với comment blocking.
