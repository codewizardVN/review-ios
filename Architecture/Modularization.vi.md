[English](./Modularization.md) | [Tiếng Việt](./Modularization.vi.md)

[← Architecture](./README.vi.md)

# Modularization

## Ý chính

Tách app thành các Swift package hoặc target riêng biệt để giảm coupling, tăng tốc build và tạo ranh giới rõ ràng giữa các tính năng.

## Chiến lược tách module phổ biến

- **Theo tầng** — `CoreDomain`, `DataLayer`, `UIComponents`
- **Theo tính năng** — `FeedFeature`, `ProfileFeature`, `AuthFeature`
- **Kết hợp** — feature modules + shared core modules

## Lợi ích

- Build tăng dần nhanh hơn (chỉ build lại module bị thay đổi)
- Ranh giới cứng ngăn coupling ngoài ý muốn giữa features
- Các team có thể sở hữu module độc lập

## Câu hỏi thực hành

- Tiêu chí nào để tách module đầu tiên?
- Ranh giới module nên chia theo tính năng hay theo tầng?

## Câu hỏi luyện tập

- Bạn dùng tiêu chí gì để tách module đầu tiên?
- Ranh giới module nên tách theo feature hay theo layer?

## Góc nhìn Senior

Bắt đầu modularize khi build time ảnh hưởng năng suất hoặc khi ownership team trở nên không rõ ràng — không phải mặc định từ ngày đầu. Over-modularization thêm overhead quản lý dependency mà không có lợi ích tương xứng với codebase nhỏ.

## Bài tập

Thiết kế module map (ASCII diagram trong comment) cho e-commerce app với: Auth, ProductCatalog, Cart, Orders, UserProfile. Xác định module nào là feature module vs shared core module (DesignSystem, Networking, Analytics). Vẽ dependency arrows. Đánh dấu dependency nào sẽ tạo circular dependency. Giải thích pain point cụ thể nào — build time, coupling, hay ownership — sẽ thúc đẩy bạn tách module đầu tiên.
