[English](./BackgroundExecution.md) | [Tiếng Việt](./BackgroundExecution.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# Background Execution

## Ý chính

iOS chỉ cho app một lượng thời gian chạy nền nhỏ và không thể đoán trước. Hệ thống — chứ không phải app của bạn — quyết định khi nào background task thực sự chạy, nên bất kỳ thiết kế nào giả định có lịch chạy đảm bảo đều sai.

## Những điều cần nắm

- `beginBackgroundTask(withName:expirationHandler:)` — mua thêm vài giây/phút để hoàn tất công việc đang dở khi vào background; luôn phải đăng ký expiration handler và kết thúc task một cách tường minh
- `BGAppRefreshTask` — refresh nền ngắn, định kỳ (ví dụ pre-fetch nội dung feed); được lên lịch qua `BGTaskScheduler`, không có khoảng thời gian đảm bảo, ngân sách tính bằng phút chứ không ít hơn
- `BGProcessingTask` — bảo trì nền dài hơn (ví dụ dọn database, re-index lớn); có thể yêu cầu ràng buộc về nguồn điện/mạng, thường chạy ban đêm khi đang sạc
- Background URLSession — download/upload tiếp tục chạy kể cả khi app bị suspend hoặc terminate, được resume qua `application(_:handleEventsForBackgroundURLSession:completionHandler:)`
- Thời điểm đăng ký task — identifier của `BGTaskScheduler` phải được đăng ký trong `Info.plist` và request thực thi trước khi `applicationDidFinishLaunching` return
- Các yếu tố hệ thống throttle — mức pin, Low Power Mode, tần suất user mở app, pattern sử dụng thiết bị; không cái nào bạn kiểm soát trực tiếp được
- Test background task — giả lập một lần chạy `BGTaskScheduler` qua LLDB (`e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:...]`) vì chờ trigger thật không thực tế

## Ví dụ

```swift
func scheduleFeedRefresh() {
    let request = BGAppRefreshTaskRequest(identifier: "com.app.feed.refresh")
    request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)
    try? BGTaskScheduler.shared.submit(request)
}

func handleFeedRefresh(task: BGAppRefreshTask) {
    scheduleFeedRefresh() // luôn reschedule task tiếp theo trước
    let operation = FeedRefreshOperation()
    task.expirationHandler = { operation.cancel() }
    operation.completionBlock = { task.setTaskCompleted(success: !operation.isCancelled) }
    OperationQueue().addOperation(operation)
}
```

## Câu hỏi luyện tập

- Tại sao phải reschedule một `BGAppRefreshTask` ngay đầu handler thay vì ở cuối?
- Sự khác biệt về đảm bảo giữa background URLSession upload và `BGProcessingTask` là gì?
- Tại sao `beginBackgroundTask` không thể thay thế cho `BGTaskScheduler`?

## Góc nhìn Senior

Cái bẫy phỏng vấn ở đây là thiết kế như thể background execution đáng tin cậy. Câu trả lời tốt coi thời gian background là cơ hội và best-effort: app phải hoàn toàn đúng đắn ngay cả khi background task không bao giờ chạy, và việc chạy nền chỉ tồn tại để làm cho *lần mở app tiếp theo* nhanh hơn hoặc mới hơn — không bao giờ để đảm bảo một side effect đã xảy ra.

## Bài tập

Thiết kế chiến lược background cho một app ghi chú cần sync các note đã sửa cục bộ lên server. Nêu rõ: việc nào thuộc `beginBackgroundTask` và việc nào thuộc `BGProcessingTask`, chuyện gì xảy ra nếu sync task bị kill giữa lúc upload, làm sao tránh upload trùng một note hai lần, và UI thể hiện trạng thái "đã sync lần cuối" trung thực ra sao khi background sync có thể đã không chạy trong nhiều giờ.
