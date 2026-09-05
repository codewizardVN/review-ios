[English](./PushNotifications.md) | [Tiếng Việt](./PushNotifications.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# Push Notifications

## Ý chính

APNs chỉ giao payload; app quyết định làm gì với nó. Registration, authorization, và contract payload với backend quan trọng không kém phần UI cuối cùng hiển thị notification.

## Những điều cần nắm

- Luồng registration — `registerForRemoteNotifications()`, nhận device token, gửi token đó lên backend
- `UNUserNotificationCenter` — request authorization, delegate method `willPresent` (foreground) và `didReceive` (tap/action)
- Notification category và action — nút action tùy chỉnh trên notification (ví dụ "Reply", "Mark as read")
- Silent/background push — `content-available: 1`, trigger `application(_:didReceiveRemoteNotification:fetchCompletionHandler:)` để refresh dữ liệu ở background, bị hệ thống throttle
- Notification Service Extension — biến đổi payload trước khi hiển thị (ví dụ giải mã nội dung, tải và đính kèm ảnh) trong ngân sách ~30 giây
- Rich notification — `UNNotificationContentExtension` cho UI tùy chỉnh
- Provisional authorization — giao lặng lẽ vào Notification Center mà không cần prompt xin quyền
- Deep link từ tap — route payload `userInfo` vào navigation của app, kể cả khi app bị cold-launch bởi cú tap

## Ví dụ

```swift
func userNotificationCenter(
    _ center: UNUserNotificationCenter,
    didReceive response: UNNotificationResponse,
    withCompletionHandler completionHandler: @escaping () -> Void
) {
    let userInfo = response.notification.request.content.userInfo
    if let orderId = userInfo["orderId"] as? String {
        router.navigate(to: .orderDetail(orderId))
    }
    completionHandler()
}
```

## Câu hỏi luyện tập

- Tại sao silent push không đáng tin cậy cho các cập nhật background mang tính thời gian thực?
- Bạn sẽ test luồng tap-to-navigate như thế nào khi app đã bị terminate hoàn toàn?

## Góc nhìn Senior

Hai điểm phân biệt câu trả lời tốt ở đây: (1) coi payload notification như một contract có version với backend — một thay đổi schema ở bên nào đó mà không phối hợp sẽ âm thầm làm gãy navigation hoặc crash các version app cũ, và (2) hiểu rằng silent push không được đảm bảo giao đúng lúc hay chắc chắn — nó bị hệ thống throttle dựa trên pattern sử dụng app, pin, và điều kiện mạng, nên không thể là cơ chế duy nhất cho bất cứ điều gì nhạy cảm về thời gian.

## Bài tập

Thiết kế schema payload và logic routing cho một app chat: một push notification cho phép user tap để nhảy thẳng đến một conversation cụ thể, và một silent push cập nhật badge số tin chưa đọc ở background. Nêu rõ JSON payload cho cả hai, cách bạn version schema để các version app cũ không crash khi gặp field lạ, và fallback nào xảy ra nếu conversation đích đã bị xóa ở server trước khi user tap.
