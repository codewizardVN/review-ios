[English](./Refactoring.md) | [Tiếng Việt](./Refactoring.vi.md)

[← Chủ đề Senior](./README.vi.md)

# Chiến lược Refactoring

## Khi nào nên Refactor

- Trước khi thêm tính năng vào vùng sẽ khó thay đổi hơn
- Khi cùng một bug xuất hiện lặp lại trong cùng module
- Khi onboarding engineer mới liên tục cần giải thích cùng một vùng khó hiểu
- Khi test coverage bằng 0 và code cần được thay đổi

## Khi nào KHÔNG nên Refactor

- Ngay trước deadline release
- Khi code đang hoạt động và không được chạm vào
- Như điều kiện tiên quyết cho tất cả công việc khác ("không thể thêm tính năng cho đến khi refactor tất cả")

## Các cách tiếp cận

- **Strangler Fig** — xây hệ thống mới song song với cũ, dần dần chuyển traffic, xóa code cũ khi xong
- **Extract and redirect** — tách logic vào module/class mới, chuyển hướng caller từng cái một
- **Characterization tests** — viết test để ghi lại behavior hiện tại trước khi thay đổi

## Câu hỏi thực hành

- Khi nào refactor và khi nào để code như cũ?
- Bạn refactor legacy codebase mà không phá vỡ behavior hiện tại như thế nào?

## Góc nhìn senior

Refactor mà không có test thì nguy hiểm. Bước đầu tiên gần như luôn là: thêm test cho behavior hiện tại, rồi mới thay đổi. Characterization test ghi lại behavior hiện tại — kể cả bug — để bạn biết khi nào có gì đó thay đổi.

## Bài tập

Chọn `MassiveViewController` trong project (hoặc tạo một cái giả với 400+ dòng). Viết characterization test cho ba behavior quan trọng nhất. Sau đó tách một trách nhiệm ra class mới dùng Strangler Fig pattern. Xác minh tất cả test vẫn pass sau khi tách.
