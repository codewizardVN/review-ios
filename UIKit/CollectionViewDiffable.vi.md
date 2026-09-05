[English](./CollectionViewDiffable.md) | [Tiếng Việt](./CollectionViewDiffable.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# Collection View và Diffable Data Source

## Ý chính

`UICollectionViewDiffableDataSource` giúp việc cập nhật list dễ lý giải hơn bằng cách mô tả state snapshot, thay vì tự tính insert và delete thủ công.

## Cần ôn

- Item identity ổn định
- Chi phí khi apply snapshot
- Cell reuse và cấu hình cell
- Mô hình section

## Câu hỏi thực hành

- Vì sao diffable vẫn có thể chậm trên list lớn?
- Điều gì hỏng nếu item identifier không ổn định?

## Câu hỏi luyện tập

- Tại sao diffable vẫn có thể cảm giác chậm trên list lớn?
- Điều gì sẽ hỏng nếu item identifier không ổn định?

## Góc nhìn senior

Diffable data source cải thiện correctness, không phải phép màu performance. Bạn vẫn cần item identity tốt, tần suất apply snapshot hợp lý, và cell configuration đủ nhẹ.

## Bài tập

Thiết kế một collection view hai section cho notifications: `unread` và `read`. Định nghĩa item identifier và giải thích cách cập nhật một item từ unread sang read mà không tạo animation khó hiểu.
