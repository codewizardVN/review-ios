[English](./DeepLinks.md) | [Tiếng Việt](./DeepLinks.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# Deep Link, Universal Link, và Notification Flow

## Ý chính

Các entry point từ bên ngoài nên được map vào app route một cách ổn định, kể cả khi app vừa cold launch, đang ở background, hay đang nằm trong một flow khác.

## Cần ôn

- URL parsing và route modeling
- Authentication gating
- Hoãn navigation tới khi app state sẵn sàng
- Push notification như một navigation intent

## Câu hỏi thực hành

- Điều gì xảy ra nếu deep link đến trước khi login xong?
- Route parsing nên nằm ở đâu?

## Câu hỏi luyện tập

- Chuyện gì xảy ra nếu deep link đến trước khi login hoàn tất?
- Việc parse route nên nằm ở đâu?

## Góc nhìn senior

Xử lý deep link là bài toán điều phối cấp app. Câu trả lời tốt nên nói về route modeling, readiness check, fallback behavior, và analytics, không chỉ là mở thẳng một screen.

## Bài tập

Thiết kế routing cho `myapp://orders/123` và một universal link tới cùng order đó. Giải thích app sẽ hoạt động thế nào khi cold launch, khi đang ở tab khác, và khi user chưa đăng nhập.
