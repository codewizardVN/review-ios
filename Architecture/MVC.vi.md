[English](./MVC.md) | [Tiếng Việt](./MVC.vi.md)

[← Architecture](./README.vi.md)

# MVC (Model-View-Controller)

## Ý chính

Pattern mặc định trong UIKit apps. Controller là cầu nối giữa Model (data/business logic) và View (UI).

## Ưu điểm

- Đơn giản để bắt đầu
- Quen thuộc với hầu hết iOS developer
- Hoạt động tốt cho các màn hình nhỏ, độc lập

## Hạn chế

- Controller có xu hướng phình to ("Massive View Controller")
- Khó unit test vì controller gắn chặt với UIKit lifecycle
- Business logic, navigation và UI thường dồn vào cùng một chỗ

## Góc nhìn Senior

MVC không hỏng về bản chất — nó thường bị áp dụng sai. MVC có kỷ luật với thin controller, model layer riêng biệt và service được tách ra có thể bảo trì được. Vấn đề thực sự là UIKit khiến việc đổ tất cả vào controller trở nên quá dễ.

## Bài tập

Lấy `ProductListViewController` (1) gọi URLSession trực tiếp, (2) format giá inline, (3) push sang detail screen. Xác định cái gì thuộc Model, Controller và một Service riêng biệt. Phác thảo sự phân tách trong comment — không cần viết code đầy đủ. Sau đó giải thích cái gì có thể unit test nếu code được cấu trúc như vậy, và cái gì vẫn không thể test trong UIKit MVC.
