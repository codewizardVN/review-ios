[English](./AutoLayout.md) | [Tiếng Việt](./AutoLayout.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# Auto Layout

## Ý chính

Auto Layout là một hệ constraint. Layout ổn định đến từ priority rõ ràng, hiểu `intrinsicContentSize`, và tránh constraint mơ hồ hoặc xung đột.

## Cần ôn

- Constraint priority
- `contentHuggingPriority` và `contentCompressionResistancePriority`
- Điểm mạnh và giới hạn của `UIStackView`
- Cách debug unsatisfiable constraints

## Câu hỏi thực hành

- Vì sao label bị compress ngoài ý muốn?
- Khi nào nên dùng `UIStackView`, khi nào không?

## Câu hỏi luyện tập

- Tại sao một label bị nén lại ngoài ý muốn?
- Khi nào nên dùng UIStackView và khi nào không?

## Góc nhìn senior

Phần lớn lỗi layout không phải vì “Auto Layout bị hỏng”. Chúng là vấn đề về ownership và định nghĩa constraint. Câu trả lời senior nên nối triệu chứng với quy tắc đang xung đột.

## Bài tập

Xây một profile header gồm avatar, name, subtitle, và action button. Giải thích cách đặt priority để tên dài vẫn truncate đúng còn button vẫn đủ vùng chạm.
