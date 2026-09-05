[English](./AppLifecycle.md) | [Tiếng Việt](./AppLifecycle.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# App Lifecycle

## Ý chính

Các lifecycle event của app cho biết khi nào app launch, active, chuyển xuống background, và quay lại foreground. Đây là nơi persistence, refresh, analytics, và security behavior thường được gắn vào.

## Cần ôn

- Trách nhiệm của `UIApplicationDelegate`
- Lifecycle theo scene với `UISceneDelegate`
- Chuyển trạng thái foreground/background
- Điều gì nên và không nên xảy ra lúc launch

## Câu hỏi thực hành

- App nên làm gì khi vào background?
- Nên refresh critical state ở đâu khi quay lại foreground?

## Câu hỏi luyện tập

- Chuyện gì nên xảy ra khi app vào background?
- Bạn refresh state quan trọng ở đâu khi quay lại foreground?

## Góc nhìn senior

Lifecycle code nên mỏng. Tầng delegate chỉ nên điều phối app-level services, còn logic của feature nên nằm trong object chuyên trách để app dễ test và dễ maintain.

## Bài tập

Liệt kê các hành động app của bạn nên làm khi cold launch, khi xuống background, và khi quay lại foreground. Sau đó tách rõ phần nào là app-level orchestration và phần nào là feature-level behavior.
