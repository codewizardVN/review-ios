[English](./Coordinator.md) | [Tiếng Việt](./Coordinator.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# Coordinator và Router

## Ý chính

Navigation là application flow, không phải view rendering. Coordinator hoặc router pattern giúp screen không phải sở hữu quá nhiều hiểu biết về phần còn lại của app.

## Cần ôn

- Root coordinator vs child coordinator
- Cách screen gửi ý định navigation lên trên
- Deep link đi vào flow đang tồn tại như thế nào
- Ownership và lifetime của coordinator

## Câu hỏi thực hành

- Khi nào screen nên trigger navigation trực tiếp?
- Ai nên phản ứng với deep link mở vào nested flow?

## Góc nhìn senior

Coordinator pattern hữu ích khi độ phức tạp của navigation là có thật. Nếu chỉ có một flow đơn giản, thêm layer có thể không đáng. Điểm quan trọng là mức độ indirection phải khớp với độ phức tạp của sản phẩm.

## Bài tập

Lấy một checkout flow gồm cart, shipping, payment, và confirmation screen. Phác thảo một root coordinator cùng một child coordinator. Sau đó giải thích deep link nên đi vào flow này ở điểm nào.
