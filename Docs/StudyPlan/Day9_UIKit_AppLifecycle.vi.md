[English](./Day9_UIKit_AppLifecycle.md) | [Tiếng Việt](./Day9_UIKit_AppLifecycle.vi.md)

# Day 9: UIKit và App Lifecycle

## Goal

Ôn lại UIKit lifecycle và các chủ đề navigation cấp app vẫn xuất hiện nhiều trong phỏng vấn senior iOS và khi debug production.

## Topics

- App lifecycle
- ViewController lifecycle
- Coordinator / Router
- Auto Layout
- CollectionView và Diffable Data Source
- Deep link
- Universal link
- Notification flow

## What You Should Be Able To Explain

- Điều gì nên nằm trong `AppDelegate` hoặc `SceneDelegate`
- Sự khác nhau giữa `viewDidLoad`, `viewWillAppear`, và `viewDidAppear`
- Vì sao Coordinator giúp làm rõ flow ownership
- Cách lý giải ambiguous hoặc conflicting constraints
- Route từ bên ngoài nên đi vào app an toàn thế nào

## Practice Questions

- App nên làm gì khi quay lại từ background?
- Vì sao deep link thường khó hơn flow push thông thường?
- Làm sao quyết định khi nào một screen nên sở hữu navigation?

## Senior Notes

- Câu hỏi UIKit thường thực chất là câu hỏi về ownership, lifecycle timing, và flow coordination.
- Câu trả lời tốt sẽ nối callback với product behavior, không chỉ đọc tên API.
