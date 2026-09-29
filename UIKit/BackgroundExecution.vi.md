[English](./BackgroundExecution.md) | [Tiếng Việt](./BackgroundExecution.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# Background Execution

## Ý chính

iOS chỉ cho app một lượng thời gian chạy nền nhỏ và không thể đoán trước. Hệ thống — chứ không phải app của bạn — quyết định khi nào background task thực sự chạy, nên bất kỳ thiết kế nào giả định có lịch chạy đảm bảo đều sai.

## Những điều cần nắm

- `beginBackgroundTask(withName:expirationHandler:)` — xin thêm một khoảng thời gian ngắn (thường khoảng 30 giây trên iOS hiện tại, không được đảm bảo) để hoàn tất công việc đang dở khi vào background; luôn phải đăng ký expiration handler và kết thúc task một cách tường minh
- `BGAppRefreshTask` — refresh nền ngắn, định kỳ (ví dụ pre-fetch nội dung feed); được lên lịch qua `BGTaskScheduler`, không có khoảng thời gian đảm bảo; mỗi lần chạy chỉ có ngân sách ngắn, khoảng 30 giây, nên chỉ hợp cho việc nhẹ
- `BGProcessingTask` — bảo trì nền dài hơn (ví dụ dọn database, re-index lớn); được chạy lâu hơn (có thể vài phút), có thể yêu cầu ràng buộc về nguồn điện/mạng (`requiresExternalPower`, `requiresNetworkConnectivity`), thường chạy khi máy rảnh, ví dụ ban đêm lúc đang sạc
- Background URLSession — download/upload tiếp tục chạy kể cả khi app bị suspend hoặc terminate, được resume qua `application(_:handleEventsForBackgroundURLSession:completionHandler:)`
- `BGContinuedProcessingTask` (iOS 26+) — cho việc do user chủ động bắt đầu khi app đang ở foreground (ví dụ export video) và cần chạy tiếp khi user rời app; hệ thống hiện tiến trình trong UI hệ thống, app phải cập nhật `progress`, và user có thể hủy
- Thời điểm đăng ký task — mỗi identifier phải được khai báo trong `BGTaskSchedulerPermittedIdentifiers` của `Info.plist`, và handler phải được đăng ký bằng `BGTaskScheduler.shared.register(forTaskWithIdentifier:using:launchHandler:)` trước khi `application(_:didFinishLaunchingWithOptions:)` return. Còn việc `submit` request thì làm lúc nào cũng được
- Các yếu tố hệ thống throttle — mức pin, Low Power Mode, tần suất user mở app, pattern sử dụng thiết bị; không cái nào bạn kiểm soát trực tiếp được
- Test background task — giả lập một lần chạy `BGTaskScheduler` qua LLDB (`e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:...]`) vì chờ trigger thật không thực tế; tương tự có `_simulateExpirationForTaskWithIdentifier:` để test expiration handler. Cần chạy trên máy thật, vì `BGTaskScheduler` không hoạt động trên Simulator

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

## Đáp án câu hỏi luyện tập

### Tại sao phải reschedule một `BGAppRefreshTask` ngay đầu handler thay vì ở cuối?

Phải reschedule ngay đầu handler vì phần cuối có thể không bao giờ chạy tới. Nếu nó không chạy, chuỗi refresh bị đứt và app sẽ không được đánh thức nữa cho tới khi user tự mở app. Mỗi `BGAppRefreshTaskRequest` chỉ dùng được một lần. Hệ thống chạy nó xong là hết, không tự lặp lại, nên muốn refresh định kỳ thì mỗi lần chạy phải tự lên lịch cho lần sau.

Có nhiều lý do khiến cuối handler không được chạy:

- Hệ thống hết ngân sách thời gian và gọi `expirationHandler`. Trong ví dụ, `FeedRefreshOperation` bị cancel và code sau đó có thể không chạy như bạn nghĩ.
- Network request bị treo, completion không bao giờ được gọi.
- App bị crash hoặc bị kill vì dùng quá nhiều bộ nhớ ở background.

Vì thế ví dụ gọi `scheduleFeedRefresh()` ở dòng đầu tiên của `handleFeedRefresh(task:)`. Submit request mới với cùng identifier sẽ thay thế request cũ đang chờ, nên không lo bị trùng lịch. Cũng nên gọi `scheduleFeedRefresh()` khi app vào background, để lần đầu tiên luôn có một request được lên lịch.

Trade-off: `earliestBeginDate` chỉ là "không sớm hơn thời điểm này", không phải lịch chạy. Đặt 15 phút không có nghĩa app sẽ chạy mỗi 15 phút. Hệ thống có thể chạy sau vài giờ, hoặc không chạy với app mà user ít mở.

### Sự khác biệt về đảm bảo giữa background URLSession upload và `BGProcessingTask` là gì?

Background URLSession đảm bảo transfer sẽ được hệ thống tiếp tục cho tới khi xong, kể cả khi app bị suspend hoặc bị hệ thống terminate. `BGProcessingTask` chỉ là một yêu cầu "hãy cho tôi chạy lúc nào đó", có thể chạy muộn hoặc không bao giờ chạy.

Cơ chế khác nhau ở chỗ ai làm việc:

- **Background URLSession:** app giao transfer cho một process của hệ thống. Process đó tự upload, tự retry khi mạng quay lại, dù app không còn chạy. Khi xong, hệ thống đánh thức hoặc launch lại app và gọi `application(_:handleEventsForBackgroundURLSession:completionHandler:)` để báo kết quả. Điều kiện: upload phải đi từ file (`uploadTask(with:fromFile:)`), không dùng data task hay async `upload(for:from:)` được.
- **`BGProcessingTask`:** code chạy trong chính process của app, chỉ khi hệ thống cho phép (thường là ban đêm, đang sạc nếu bạn đặt `requiresExternalPower`). Nó có thể bị dừng bất cứ lúc nào qua `expirationHandler`.

Với app ghi chú trong bài tập, phần upload note nên đi qua background URLSession, còn `BGProcessingTask` hợp cho việc như dọn dẹp dữ liệu hoặc tạo lại index. Trade-off: background URLSession cũng không phải tức thì. Transfer có thể được hệ thống hoãn, nhất là khi đặt `isDiscretionary = true`, và nếu user force-quit app thì các transfer đang chờ bị hủy.

### Tại sao `beginBackgroundTask` không thể thay thế cho `BGTaskScheduler`?

Vì `beginBackgroundTask` chỉ kéo dài thời gian chạy ngay lúc app vừa vào background, còn `BGTaskScheduler` là cách để hệ thống đánh thức app vào một lúc sau. Hai API giải quyết hai vấn đề khác nhau.

`beginBackgroundTask(withName:expirationHandler:)` nói với hệ thống: "tôi đang làm dở việc này, đừng suspend tôi ngay". App được thêm một khoảng thời gian ngắn, thường khoảng 30 giây trên iOS hiện tại, nhưng không được đảm bảo. Hãy đọc `UIApplication.shared.backgroundTimeRemaining` thay vì giả định một con số. App phải gọi `endBackgroundTask` khi xong việc, hoặc muộn nhất là trong `expirationHandler` trước khi hết thời gian, nếu không sẽ bị kill. Nó không thể:

- Bắt đầu công việc mới vào ba tiếng sau.
- Đánh thức app đã bị suspend hoặc terminate.
- Chạy công việc dài hàng phút.

`BGTaskScheduler` thì lên lịch để hệ thống launch hoặc đánh thức app sau này, với ngân sách riêng. Trong bài tập, `beginBackgroundTask` dùng để lưu note đang sửa và bắt đầu upload khi user vừa thoát app, còn việc sync bù định kỳ để `BGTaskScheduler` lo. Từ iOS 26 còn có `BGContinuedProcessingTask` cho việc do user chủ động bắt đầu (như export) và muốn chạy tiếp khi app vào background. Request phải được submit khi app đang ở foreground, hệ thống hiển thị tiến trình dựa trên `progress` mà app cập nhật, và user có thể hủy task. Nó không phải cách để app tự chạy nền theo lịch. Trade-off: gọi `beginBackgroundTask` cho mọi thứ không làm app chạy lâu hơn, chỉ làm app dễ bị kill hơn nếu quên kết thúc task.

## Bẫy phỏng vấn

### "Quên gọi endBackgroundTask thì sao, hết giờ hệ thống tự dừng thôi mà?"

**Dễ trả lời sai:** Không sao, hết thời gian thì hệ thống tự kết thúc task và suspend app bình thường.

**Nên trả lời:** Nếu hết thời gian mà task chưa được kết thúc, hệ thống sẽ kill app thay vì suspend. Lần sau user mở app sẽ là cold launch và mất state, trong crash log có thể thấy lý do liên quan tới background task assertion. `expirationHandler` phải dừng công việc và gọi `endBackgroundTask(taskID)`, và đường hoàn tất bình thường cũng phải gọi nó đúng một lần. Nên bọc trong helper để hai đường không bị quên hoặc gọi hai lần.

### "Có thể register BGTaskScheduler handler ở bất cứ đâu, ví dụ khi user bật setting sync?"

**Dễ trả lời sai:** Được, register lúc nào cần cũng được, miễn là trước khi submit request.

**Nên trả lời:** Handler phải được register trước khi `application(_:didFinishLaunchingWithOptions:)` return. Khi hệ thống launch app ở background để chạy task, nó cần tìm thấy handler ngay lúc launch. Register muộn sẽ gây exception, và identifier cũng phải có trong `BGTaskSchedulerPermittedIdentifiers` của Info.plist. Setting của user chỉ nên quyết định có submit request hay không, còn register thì luôn làm lúc launch.

### "Đặt earliestBeginDate 15 phút thì feed được refresh mỗi 15 phút?"

**Dễ trả lời sai:** Đúng, đó là tần suất refresh của app.

**Nên trả lời:** `earliestBeginDate` chỉ là mốc sớm nhất, hệ thống quyết định thời điểm thật dựa trên tần suất user mở app, pin, mạng và Low Power Mode. App ít dùng có thể không được chạy trong nhiều ngày. Nếu user tắt Background App Refresh trong Settings hoặc force-quit app thì task không chạy. UI phải hiển thị trung thực kiểu "Cập nhật lần cuối: 3 giờ trước" và app vẫn phải refresh khi vào foreground.

## Bài tập

Thiết kế chiến lược background cho một app ghi chú cần sync các note đã sửa cục bộ lên server. Nêu rõ: việc nào thuộc `beginBackgroundTask` và việc nào thuộc `BGProcessingTask`, chuyện gì xảy ra nếu sync task bị kill giữa lúc upload, làm sao tránh upload trùng một note hai lần, và UI thể hiện trạng thái "đã sync lần cuối" trung thực ra sao khi background sync có thể đã không chạy trong nhiều giờ.
