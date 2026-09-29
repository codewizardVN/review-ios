[English](./PushNotifications.md) | [Tiếng Việt](./PushNotifications.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# Push Notifications

## Ý chính

APNs chỉ giao payload; app quyết định làm gì với nó. Registration, authorization, và contract payload với backend quan trọng không kém phần UI cuối cùng hiển thị notification.

## Những điều cần nắm

- Luồng registration — `registerForRemoteNotifications()`, nhận device token, gửi token đó lên backend
- `UNUserNotificationCenter` — request authorization, delegate method `willPresent` (foreground) và `didReceive` (tap/action)
- Notification category và action — nút action tùy chỉnh trên notification (ví dụ "Reply", "Mark as read")
- Silent/background push — `content-available: 1`, trigger `application(_:didReceiveRemoteNotification:fetchCompletionHandler:)` để refresh dữ liệu ở background (cần bật Background Modes > Remote notifications), bị hệ thống throttle
- Notification Service Extension — biến đổi payload trước khi hiển thị (ví dụ giải mã nội dung, tải và đính kèm ảnh) trong ngân sách ~30 giây
- Rich notification — `UNNotificationContentExtension` cho UI tùy chỉnh
- Provisional authorization (iOS 12+) — xin quyền với option `.provisional`: không hiện prompt, notification được giao lặng lẽ vào Notification Center, và user tự chọn giữ hay tắt ngay trên notification
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
        router.navigate(to: .orderDetail(id: orderId))
    }
    completionHandler()
}
```

## Câu hỏi luyện tập

- Tại sao silent push không đáng tin cậy cho các cập nhật background mang tính thời gian thực?
- Bạn sẽ test luồng tap-to-navigate như thế nào khi app đã bị terminate hoàn toàn?

## Góc nhìn Senior

Hai điểm phân biệt câu trả lời tốt ở đây: (1) coi payload notification như một contract có version với backend — một thay đổi schema ở bên nào đó mà không phối hợp sẽ âm thầm làm gãy navigation hoặc crash các version app cũ, và (2) hiểu rằng silent push không được đảm bảo giao đúng lúc hay chắc chắn — nó bị hệ thống throttle dựa trên pattern sử dụng app, pin, và điều kiện mạng, nên không thể là cơ chế duy nhất cho bất cứ điều gì nhạy cảm về thời gian.

## Đáp án câu hỏi luyện tập

### Tại sao silent push không đáng tin cậy cho các cập nhật background mang tính thời gian thực?

Silent push không đáng tin vì iOS coi nó là "gợi ý nên cập nhật", không phải lệnh bắt buộc. Hệ thống có quyền trì hoãn, gộp, hoặc bỏ hẳn nó. Một silent push (`content-available: 1`, header `apns-push-type: background`, `apns-priority: 5`) chỉ đánh thức app nếu hệ thống thấy hợp lý.

Những lý do khiến nó không đến hoặc đến muộn:

- **Throttle.** Apple khuyến cáo không gửi quá vài cái mỗi giờ. Gửi nhiều hơn thì hệ thống bỏ bớt, nhất là khi pin yếu, bật Low Power Mode, hoặc user ít mở app.
- **User force-quit app.** Nếu user vuốt tắt app trong app switcher, silent push sẽ không đánh thức app cho tới khi user tự mở lại.
- **Gộp khi offline.** Khi thiết bị không có mạng, APNs chỉ giữ notification mới nhất cho mỗi app. Các cái cũ hơn mất luôn.
- **Thời gian chạy ngắn.** Khi được đánh thức, app chỉ có khoảng 30 giây để xử lý và gọi completion handler.

Vì vậy, với thứ nhạy cảm về thời gian như tin nhắn chat, hãy gửi alert push hiển thị được. Nếu cần xử lý nội dung (giải mã, tải ảnh) thì dùng Notification Service Extension, vì nó chạy cho mọi alert push có `mutable-content: 1`. Gọi điện VoIP dùng PushKit kết hợp CallKit, cập nhật trạng thái realtime trên màn hình khóa dùng push của Live Activity. Silent push chỉ nên dùng để làm dữ liệu "mới hơn" cho lần mở app tiếp theo. Khi app quay lại foreground, vẫn phải tự fetch lại.

### Bạn sẽ test luồng tap-to-navigate như thế nào khi app đã bị terminate hoàn toàn?

Cách test là tắt hẳn app, gửi một push thật hoặc giả lập, tap vào nó, và để Xcode attach debugger đúng lúc app được launch. Trường hợp cold launch đi qua một code path khác hẳn so với khi app đang chạy, nên phải test riêng.

Các bước thực tế:

1. Trong Xcode, vào Edit Scheme, Run, Info, chọn "Wait for the executable to be launched". Xcode sẽ chờ và attach khi app được hệ thống mở.
2. Gửi push. Trên simulator có thể dùng `xcrun simctl push booted <bundle-id> payload.apns` hoặc kéo thả file `.apns` vào simulator. Trên máy thật, gửi qua APNs sandbox bằng device token debug.
3. Tap notification, đặt breakpoint trong `userNotificationCenter(_:didReceive:withCompletionHandler:)`.

Những điều cần kiểm tra:

- `UNUserNotificationCenter.current().delegate` phải được gán trước khi `application(_:didFinishLaunchingWithOptions:)` return. Gán muộn hơn thì `didReceive` không được gọi cho cú tap đã launch app.
- `router.navigate(to: .orderDetail(id: orderId))` trong ví dụ có thể chạy khi UI chưa dựng xong. Router cần giữ route lại cho tới khi app sẵn sàng.

Phần parse `userInfo` thành route nên tách thành hàm thuần để unit test với payload giả, còn cold launch thì test thủ công hoặc UI test. Trade-off: UI test với push thật khá mong manh, nên giữ số lượng ít và tập trung vào các payload quan trọng.

## Bẫy phỏng vấn

### "User đã vuốt tắt app, silent push vẫn đánh thức app để sync chứ?"

**Dễ trả lời sai:** Có, silent push được thiết kế để chạy ở background nên luôn đánh thức app.

**Nên trả lời:** Không. Khi user chủ động force-quit từ app switcher, iOS hiểu là user không muốn app chạy nền. Silent push và background fetch sẽ không launch app cho tới khi user mở app lại. Alert push vẫn hiển thị bình thường, và Notification Service Extension vẫn chạy vì nó là process riêng. Nếu nghiệp vụ cần chắc chắn user thấy thông tin, hãy gửi alert push.

### "Push đến khi app đang mở, sao không thấy banner?"

**Dễ trả lời sai:** Do APNs không gửi push khi app đang ở foreground.

**Nên trả lời:** Push vẫn đến, nhưng mặc định iOS không hiện banner khi app đang ở foreground. Bạn phải implement `userNotificationCenter(_:willPresent:withCompletionHandler:)` và trả về các option muốn hiển thị. Option `.alert` đã deprecated từ iOS 14, nên dùng `.banner` và `.list`. Đây cũng là chỗ để quyết định không hiện banner nếu user đang mở đúng conversation đó.

```swift
completionHandler([.banner, .list, .sound])
```

### "Device token lấy một lần rồi lưu lại dùng mãi được không?"

**Dễ trả lời sai:** Được, token gắn với thiết bị nên không bao giờ đổi, chỉ cần gửi lên server lần đầu.

**Nên trả lời:** Token có thể đổi khi user cài lại app, khôi phục từ backup sang máy mới, hoặc khi hệ thống cấp lại. Token sandbox (build debug) và production (TestFlight, App Store) cũng khác nhau. Hãy gọi `registerForRemoteNotifications()` mỗi lần launch và gửi token lên server khi nó khác giá trị đã lưu. Server cũng phải xóa token khi APNs trả về lỗi như `410 Unregistered`.

## Bài tập

Thiết kế schema payload và logic routing cho một app chat: một push notification cho phép user tap để nhảy thẳng đến một conversation cụ thể, và một silent push cập nhật badge số tin chưa đọc ở background. Nêu rõ JSON payload cho cả hai, cách bạn version schema để các version app cũ không crash khi gặp field lạ, và fallback nào xảy ra nếu conversation đích đã bị xóa ở server trước khi user tap.
