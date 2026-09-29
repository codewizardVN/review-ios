[English](./AppLifecycle.md) | [Tiếng Việt](./AppLifecycle.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# App Lifecycle

## Ý chính

Các lifecycle event của app cho biết khi nào app launch, active, chuyển xuống background, và quay lại foreground. Đây là nơi persistence, refresh, analytics, và security behavior thường được gắn vào.

## Cần ôn

- Trách nhiệm của `UIApplicationDelegate`: những việc ở cấp process, chạy một lần cho cả app, như cấu hình service (crash reporting, analytics), đăng ký `BGTaskScheduler` handler, gán `UNUserNotificationCenter.current().delegate`, nhận device token push, và `applicationWillTerminate`. Khi app đã dùng scene, AppDelegate không còn lo UI và không nhận các sự kiện foreground/background nữa.
- Lifecycle theo scene với `UISceneDelegate` (thực tế là `UIWindowSceneDelegate`): mỗi scene là một "cửa sổ" UI của app (trên iPad có thể có nhiều scene cùng lúc). Scene delegate tạo window trong `scene(_:willConnectTo:options:)` và nhận các callback `sceneWillEnterForeground`, `sceneDidBecomeActive`, `sceneWillResignActive`, `sceneDidEnterBackground`, `sceneDidDisconnect`.
- Chuyển trạng thái foreground/background: app đi qua các trạng thái not running → inactive → active (đang nhận tương tác) → inactive → background (còn chạy code trong thời gian ngắn) → suspended (nằm trong bộ nhớ nhưng không chạy code). Từ suspended, hệ thống có thể kill app bất cứ lúc nào mà không báo trước.
- Điều gì nên và không nên xảy ra lúc launch: `application(_:didFinishLaunchingWithOptions:)` và `scene(_:willConnectTo:options:)` nằm trên đường khởi động, nên chỉ làm việc cần để hiện màn hình đầu tiên và những việc bắt buộc phải làm lúc launch (đăng ký background task, gán notification delegate, đọc URL/notification đã mở app). Việc nặng hoặc không gấp (tải config, dọn cache, khởi tạo SDK phụ) nên để sau khi UI đầu tiên đã hiện, hoặc chạy lazy khi cần.

## Câu hỏi thực hành

- App nên làm gì khi vào background?
- Nên refresh critical state ở đâu khi quay lại foreground?

## Câu hỏi luyện tập

- Chuyện gì nên xảy ra khi app vào background?
- Bạn refresh state quan trọng ở đâu khi quay lại foreground?

## Góc nhìn senior

Lifecycle code nên mỏng. Tầng delegate chỉ nên điều phối app-level services, còn logic của feature nên nằm trong object chuyên trách để app dễ test và dễ maintain.

## Đáp án câu hỏi luyện tập

### Chuyện gì nên xảy ra khi app vào background?

Khi app vào background, việc chính là lưu lại những gì user chưa kịp lưu, dừng các việc tốn tài nguyên, và che nội dung nhạy cảm, tất cả phải thật nhanh. Với app dùng scene, callback là `sceneDidEnterBackground(_:)`. Với app cũ chỉ có AppDelegate, callback là `applicationDidEnterBackground(_:)`. Callback này phải return nhanh (Apple nói khoảng 5 giây, quá lâu thì app có thể bị kill), và sau khi nó return, app sẽ sớm bị suspend nếu không xin thêm thời gian. Khi suspended, mọi thread của app bị đóng băng hẳn, không chạy tiếp như bình thường.

Những việc nên làm:

- Lưu draft, form đang nhập, vị trí đọc. Nếu dùng state restoration thì trả về `NSUserActivity` qua `stateRestorationActivity(for:)`.
- Dừng timer, animation, location update không cần thiết, pause video.
- Che màn hình nhạy cảm (số dư, OTP) trước khi hệ thống chụp snapshot cho app switcher. Nên làm từ `sceneWillResignActive(_:)` để chắc chắn kịp.
- Lên lịch `BGAppRefreshTask` nếu cần refresh sau này.

Nếu một việc cần thêm thời gian (ví dụ upload đang dở) thì bọc nó trong `beginBackgroundTask`, đừng chặn callback. Trade-off: đừng dồn logic feature vào SceneDelegate. Mỗi service nên tự lắng nghe `UIScene.didEnterBackgroundNotification` hoặc được một lifecycle coordinator gọi tới, để delegate vẫn mỏng.

### Bạn refresh state quan trọng ở đâu khi quay lại foreground?

Thường nên refresh ở `sceneWillEnterForeground(_:)`, tức là lúc app sắp hiện lại cho user. Những việc chỉ nên làm khi app thật sự nhận tương tác thì để ở `sceneDidBecomeActive(_:)`. Hai callback này khác nhau ở tần suất. `willEnterForeground` chỉ chạy khi app đi từ background lên. `didBecomeActive` chạy cả khi user kéo Control Center xuống rồi thả, khi alert hệ thống hay prompt Face ID vừa đóng. Nếu gọi API nặng trong `didBecomeActive`, bạn sẽ gọi thừa rất nhiều lần.

State "quan trọng" thường gồm:

- Token phiên đăng nhập còn hạn không. Nếu hết hạn thì yêu cầu đăng nhập lại trước khi hiện dữ liệu.
- Quyền hệ thống có thể đã bị user đổi trong Settings (notification, location, camera).
- Dữ liệu hay đổi theo thời gian: badge, số dư, feed.

Cách tốt là để SceneDelegate chỉ phát sự kiện "app đã quay lại foreground". Một `SessionManager` hoặc từng feature tự quyết định có cần refresh không, dựa trên thời điểm refresh lần cuối (ví dụ chỉ refresh nếu đã qua 5 phút). Trade-off: refresh mọi thứ mỗi lần quay lại thì an toàn nhưng tốn pin và gây nháy UI. Cần throttle và ưu tiên phần user thấy đầu tiên.

## Bẫy phỏng vấn

### "Code trong applicationDidEnterBackground của AppDelegate có chạy không?"

**Dễ trả lời sai:** Có, AppDelegate luôn nhận mọi sự kiện foreground/background, SceneDelegate chỉ là phần thêm vào.

**Nên trả lời:** Khi app đã adopt scene (có `UIApplicationSceneManifest` trong Info.plist), UIKit gọi `sceneDidEnterBackground`, `sceneWillEnterForeground`... trên SceneDelegate. Các method tương ứng trên AppDelegate không được gọi nữa. Notification cấp app như `UIApplication.didEnterBackgroundNotification` vẫn được post, nên service nào lắng nghe notification vẫn chạy. Tại WWDC25 (TN3187) Apple cũng thông báo: với iOS 26 SDK, app chưa dùng scene lifecycle chỉ bị log cảnh báo; nhưng từ bản iOS lớn tiếp theo sau iOS 26, app UIKit build bằng SDK mới nhất mà chưa adopt scene lifecycle sẽ không launch được. Điều kiện này gắn với việc build bằng SDK mới nhất, không phải chỉ với phiên bản iOS mà user đang chạy. Vì vậy code lifecycle mới nên viết theo scene.

### "Làm mới dữ liệu trong didBecomeActive có ổn không?"

**Dễ trả lời sai:** Ổn, vì `didBecomeActive` nghĩa là "app vừa quay lại từ background".

**Nên trả lời:** `didBecomeActive` chạy mỗi lần app hết bị ngắt quãng: sau khi đóng Control Center, Notification Center, alert xin quyền, prompt Face ID, hoặc cuộc gọi đến. App không hề vào background trong các trường hợp này. Đặt network refresh ở đây sẽ tạo request thừa, thậm chí vòng lặp, ví dụ Face ID prompt làm app resign active, rồi active lại, rồi lại gọi Face ID. Refresh theo nghĩa "quay lại app" thì đặt ở `sceneWillEnterForeground`. `didBecomeActive` chỉ dành cho việc như resume game, camera, animation.

### "Lưu dữ liệu trong applicationWillTerminate là đủ chứ?"

**Dễ trả lời sai:** Có, `applicationWillTerminate` (hoặc `sceneDidDisconnect`) là chỗ cuối cùng để lưu trước khi app tắt.

**Nên trả lời:** Hầu hết lần app "chết" là khi đang suspended: hệ thống thu hồi bộ nhớ, hoặc user vuốt tắt app. Lúc đó process bị kill mà không có callback nào. `applicationWillTerminate` gần như chỉ chạy khi app đang chạy ở background, chưa bị suspend. `sceneDidDisconnect` cũng không có nghĩa là app tắt: hệ thống có thể ngắt scene để lấy lại tài nguyên rồi connect lại sau. Lưu dữ liệu nên xảy ra ở `sceneDidEnterBackground` hoặc ngay khi dữ liệu thay đổi.

## Bài tập

Liệt kê các hành động app của bạn nên làm khi cold launch, khi xuống background, và khi quay lại foreground. Sau đó tách rõ phần nào là app-level orchestration và phần nào là feature-level behavior.
