[English](./TestableDesign.md) | [Tiếng Việt](./TestableDesign.vi.md)

[← Testing](./README.vi.md)

# Thiết kế có thể kiểm thử

## Các nguyên tắc giúp code dễ test

1. **Inject dependency** — không bao giờ khởi tạo dependency bên trong
2. **Phụ thuộc vào protocol, không phải implementation cụ thể** — dễ thay thế bằng fake
3. **Tách side effect** — logic thuần túy ở một chỗ, I/O ở ranh giới
4. **Tránh singleton và global state** — khiến test phụ thuộc thứ tự và dễ vỡ
5. **Đơn vị nhỏ, tập trung** — class lớn khó test vì làm quá nhiều việc

## Dấu hiệu kiến trúc không thể kiểm thử

- ViewModel gọi `URLSession.shared` trực tiếp
- Logic nằm trong `viewDidLoad` hoặc `body`
- Shared mutable global state
- Initializer khởi động service thật

## Câu hỏi thực hành

- Có nên test tất cả mọi thứ không?
- Bao nhiêu UI testing là đủ mà không trở nên flaky?

## Góc nhìn senior

Khả năng test là thước đo của thiết kế tốt. Tư duy senior tối ưu độ tin cậy trên chi phí — không phải số lượng test bằng mọi giá. Viết test ở những nơi mà failure sẽ gây đau đớn, không phải ở mọi nơi như nhau.

## Bài tập

Lấy đoạn code không thể test này: `ProfileViewController` gọi `URLSession.shared.dataTask` trực tiếp trong `viewDidLoad`. Refactor để có thể test bằng cách tách `ProfileService` protocol, inject qua initializer, và viết một unit test không chạm đến network.
