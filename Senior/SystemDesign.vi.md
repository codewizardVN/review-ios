[English](./SystemDesign.md) | [Tiếng Việt](./SystemDesign.vi.md)

[← Chủ đề Senior](./README.vi.md)

# System Design cho iOS Apps

## Cần tập trung vào gì

- Ranh giới feature và ownership của module
- Luồng dữ liệu từ API qua storage tới UI
- Yêu cầu offline và caching
- Reliability, observability, và release risk

## Một câu trả lời senior tốt

Bắt đầu từ yêu cầu sản phẩm, rồi giải thích:

- thành phần chính
- quan hệ phụ thuộc giữa chúng
- state nằm ở đâu
- failure được xử lý thế nào
- phần nào sẽ hoãn lại cho bản đầu tiên nhỏ hơn

## Tình huống ví dụ

Thiết kế một app feed có:

- API cần đăng nhập
- local cache cho item gần đây
- pagination
- pull to refresh
- hỗ trợ đọc offline

Một cách tách hợp lý:

- `FeedAPIClient` cho transport
- `FeedRepository` cho mapping và điều phối cache
- `FeedStore` cho persistence
- `FeedViewModel` hoặc reducer cho screen state
- `FeedCoordinator` cho navigation

## Câu hỏi thực hành

- Bạn tách module trong app đang lớn lên như thế nào?
- Với team hai người, bạn sẽ đơn giản hóa phần nào?

## Góc nhìn senior

Câu trả lời system design không phải để vẽ nhiều box nhất. Nó là cách thể hiện judgment: độ phức tạp nào hợp lý lúc này, phần nào nên defer, và design vẫn vận hành được ra sao khi sản phẩm lớn lên.

## Bài tập

Phác thảo một tính năng notification inbox. Gồm sync strategy, cập nhật read/unread, pagination, và điểm vào từ push notification. Sau đó giải thích phần nào bạn sẽ cố ý chưa xây ở version 1.
