[English](./WidgetsLiveActivities.md) | [Tiếng Việt](./WidgetsLiveActivities.vi.md)

[← SwiftUI](./README.vi.md)

# Widgets và Live Activities

## Ý chính

Một widget extension là một process riêng biệt với bộ nhớ và ngân sách thực thi của chính nó — nó render một snapshot của state theo timeline do hệ thống kiểm soát, không phải view sống động của app đang chạy. Live Activities mở rộng model đó cho state cập nhật real-time, thường xuyên trên Lock Screen và Dynamic Island.

## Những điều cần nắm

- `TimelineProvider` / `AppIntentTimelineProvider` — cung cấp danh sách giá trị `TimelineEntry` kèm ngày; hệ thống render entry nào có ngày đã qua, theo lịch của riêng nó, không phải của bạn
- Widget family (`systemSmall/Medium/Large`, `accessoryCircular/Rectangular/Inline`) — layout phải thích ứng theo từng family. Widget có thể được render ở các chế độ khác nhau (đọc qua `@Environment(\.widgetRenderingMode)`): accessory widget trên Lock Screen render ở chế độ `vibrant` (bỏ màu, hệ thống tự tô), và từ iOS 18 widget trên Home Screen cũng có thể ở chế độ `accented` (tinted) khi user chọn icon/widget kiểu tint, nên đừng dựa vào màu để truyền thông tin
- Chia sẻ dữ liệu — widget extension không thể truy cập in-memory state của app chính; dữ liệu phải đi qua App Group container (shared `UserDefaults`, file, hoặc SQLite/Core Data)
- `WidgetCenter.shared.reloadTimelines(ofKind:)` — cách app chính request widget refresh thay vì phụ thuộc vào timeline riêng của widget (chịu ràng buộc ngân sách reload toàn hệ thống)
- ActivityKit / Live Activities — `Activity<Attributes>`: phần tĩnh (như `orderId`) nằm trong chính struct `ActivityAttributes` và không đổi suốt đời activity, còn `ContentState` là phần động được cập nhật thường xuyên (ETA, trạng thái). Dữ liệu động gửi trong mỗi update (local hoặc push) bị giới hạn 4 KB, nên chỉ đưa vào những gì UI cần. Activity được khởi động từ app (hoặc bằng push-to-start từ iOS 17.2), cập nhật local bằng `activity.update(_:)` khi app đang chạy, hoặc qua push ActivityKit (payload `content-state`); push ưu tiên cao (`apns-priority: 10`) bị hệ thống giới hạn ngân sách, app cần cập nhật dày có thể khai báo `NSSupportsLiveActivitiesFrequentUpdates` trong Info.plist
- Vùng layout Dynamic Island — compact leading/trailing, minimal, expanded — mỗi vùng cần view riêng, và nội dung expanded vẫn phải giữ nhẹ
- Xử lý kết thúc vòng đời — một Live Activity chỉ active tối đa 8 giờ; sau đó hệ thống tự kết thúc nó, và activity đã kết thúc có thể còn hiển thị trên Lock Screen tối đa 4 giờ nữa. Bạn nên kết thúc tường minh bằng `activity.end(_:dismissalPolicy:)` hoặc push `end` khi sự kiện xong, nếu không user sẽ thấy dữ liệu stale trên Lock Screen
- Deep link — widget và Live Activity mở app qua `widgetURL(_:)` (cả widget một vùng chạm) hoặc `Link` (nhiều vùng chạm, không dùng được ở `systemSmall`), chứ không giữ tham chiếu tới state của app
- Interactive widget (iOS 17+) — `Button(intent:)` và `Toggle(isOn:intent:)` với một `AppIntent` cho phép user thao tác ngay trên widget/Live Activity mà không mở app; intent chạy, ghi dữ liệu, rồi hệ thống reload timeline để render lại. View vẫn là snapshot, không có state sống

## Ví dụ

```swift
struct DeliveryAttributes: ActivityAttributes {
    struct ContentState: Codable, Hashable {
        var etaMinutes: Int
        var status: String
    }
    var orderId: String
}

// Khởi động từ app
let activity = try Activity<DeliveryAttributes>.request(
    attributes: DeliveryAttributes(orderId: "123"),
    content: .init(state: .init(etaMinutes: 20, status: "Preparing"), staleDate: nil)
)
```

## Câu hỏi luyện tập

- Tại sao widget không thể đọc trực tiếp view model `@Observable` của app?
- Chuyện gì xảy ra với UI Live Activity trên Lock Screen nếu push update ngừng gửi đến?
- Tại sao hệ thống giới hạn tần suất `reloadTimelines` thực sự trigger redraw?

## Góc nhìn Senior

Câu hỏi về widget và Live Activity kiểm tra xem bạn có hiểu ranh giới process hay không. Sai lầm phổ biến là thiết kế widget như thể nó chỉ là một màn hình SwiftUI khác với binding sống động — không phải vậy. Câu trả lời tốt gọi tên đường đi dữ liệu thực sự (App Group, push payload, timeline entry) từ đầu đến cuối và tính đến độ "cũ" của dữ liệu: user thấy gì khi dữ liệu nền chưa refresh trong một thời gian, và thiết kế fail một cách graceful ra sao thay vì hiển thị thông tin sai một cách âm thầm.

## Đáp án câu hỏi luyện tập

### Tại sao widget không thể đọc trực tiếp view model `@Observable` của app?

Vì widget extension chạy trong một process riêng, và view model `@Observable` chỉ tồn tại trong bộ nhớ của process app — hai process không chia sẻ object với nhau.

Hãy hình dung app và widget là hai chương trình khác nhau, được đóng gói chung. Khi hệ thống cần widget, nó khởi chạy extension (có khi app hoàn toàn không chạy), gọi `TimelineProvider` để lấy entry, render view thành snapshot rồi có thể tắt extension. Không có lúc nào extension "nhìn" được vào heap của app, nên observation tracking của `@Observable` không vượt qua ranh giới này. Ngay cả khi cả hai target cùng compile một file `ViewModel.swift`, mỗi process có instance riêng.

Đường đi đúng của dữ liệu:

- App ghi state cần hiển thị vào App Group container (shared `UserDefaults` với `suiteName`, file JSON, hoặc store SwiftData/Core Data dùng chung).
- App gọi `WidgetCenter.shared.reloadTimelines(ofKind:)` sau khi ghi.
- `TimelineProvider` đọc từ App Group và tạo entry.

Trade-off: dữ liệu widget luôn là snapshot có độ trễ, nên chỉ ghi phần tối thiểu widget cần (không phải cả view model) và lưu kèm thời điểm cập nhật để widget có thể hiển thị "cập nhật lúc…" thay vì giả vờ là dữ liệu real-time.

### Chuyện gì xảy ra với UI Live Activity trên Lock Screen nếu push update ngừng gửi đến?

UI vẫn đứng yên ở `ContentState` cuối cùng nhận được — hệ thống không tự làm mới hay tự báo lỗi, nên user sẽ thấy ETA "20 phút" cho đến khi activity hết hạn (tối đa 8 giờ active, cộng thêm tối đa 4 giờ trên Lock Screen) nếu bạn không thiết kế cho trường hợp này.

Live Activity không tự chạy code hay fetch dữ liệu; nó chỉ render lại khi có update mới từ app hoặc từ push. Có ba cơ chế để xử lý độ "cũ":

- `staleDate`: đặt khi start hoặc gửi trong mỗi update (`stale-date` trong push payload). Khi quá thời điểm này, `context.isStale` thành `true` và view có thể hiển thị "Đang cập nhật…" hoặc làm mờ ETA.
- Thời lượng tối đa: sau 8 giờ hệ thống tự kết thúc activity; sau khi kết thúc nó có thể còn trên Lock Screen thêm tối đa 4 giờ (trừ khi bạn đặt dismissal policy khác hoặc user tự gỡ).
- Kết thúc tường minh: backend nên gửi event `end` kèm trạng thái cuối và `dismissal-date` khi đơn hoàn tất hoặc bị hủy.

Với bài tập 30 phút không có update: đặt `staleDate` khoảng vài phút sau ETA dự kiến, khi stale thì thay ETA bằng thông báo trung tính như "Đang chờ cập nhật từ cửa hàng" thay vì con số có thể sai.

### Tại sao hệ thống giới hạn tần suất `reloadTimelines` thực sự trigger redraw?

Vì mỗi lần reload tốn pin và tài nguyên của cả hệ thống, và widget là thứ user nhìn lướt chứ không phải màn hình real-time, nên WidgetKit coi `reloadTimelines` là một yêu cầu chứ không phải một mệnh lệnh.

Mỗi lần reload, hệ thống phải đánh thức process extension, chạy `TimelineProvider` (có thể đọc disk, gọi network), render và lưu snapshot cho mọi family đang hiển thị. Nhân lên với hàng chục widget trên một thiết bị, việc để app reload tùy ý sẽ làm hao pin rõ rệt. Vì vậy mỗi widget có một ngân sách reload hằng ngày (tài liệu Apple nêu khoảng 40–70 lần/ngày cho widget được xem thường xuyên), hệ thống gộp các request gần nhau và tự chọn thời điểm. Một số trường hợp không bị tính vào ngân sách, ví dụ khi app đang ở foreground hoặc có audio/navigation session đang chạy.

Thiết kế đúng là tránh cần reload: cung cấp nhiều entry trong tương lai ngay trong một timeline, dùng `Text(date, style: .timer)` hoặc `.relative` cho đồng hồ đếm để hệ thống tự cập nhật mà không reload, và chuyển sang Live Activity khi dữ liệu thực sự thay đổi từng phút.

## Bẫy phỏng vấn

### "Muốn widget đếm ngược từng giây thì dùng Timer hoặc reload mỗi giây?"

**Dễ trả lời sai:** Đặt `Timer.publish` / `onReceive` trong view của widget, hoặc tạo timeline với entry cách nhau một giây.

**Nên trả lời:** View của widget được render thành snapshot rồi lưu lại; không có code nào chạy liên tục bên trong nó, nên `Timer` không bao giờ bắn. Entry mỗi giây cũng lãng phí ngân sách và hệ thống không đảm bảo hiển thị đúng lúc. Hãy dùng các view mà hệ thống tự animate: `Text(endDate, style: .timer)`, `Text(timerInterval: start...end)` hoặc `ProgressView(timerInterval:)`; chúng cập nhật mỗi giây mà không cần reload.

### "View của Live Activity có thể tự gọi API để lấy ETA mới?"

**Dễ trả lời sai:** Nghĩ rằng Live Activity là một mini-app, nên view của nó có thể dùng `URLSession` hoặc nhận location update để tự làm mới.

**Nên trả lời:** Live Activity chạy trong sandbox, không truy cập network và không nhận location update. Nội dung chỉ đổi khi app gọi `activity.update(_:)` (app phải đang chạy, kể cả trong background) hoặc khi server gửi push ActivityKit (`apns-push-type: liveactivity`) chứa `content-state` mới. Vì app thường bị suspend, push từ server mới là đường cập nhật đáng tin cậy cho đơn giao hàng.

### "Chỉ có thể start Live Activity khi app đang ở foreground?"

**Dễ trả lời sai:** Khẳng định `Activity.request` là cách duy nhất, nên nếu user đặt hàng trên web thì không thể hiện Live Activity cho đến khi họ mở app.

**Nên trả lời:** Đúng với iOS 16.1–17.1, nhưng từ iOS 17.2 có push-to-start: app lấy token qua `Activity<DeliveryAttributes>.pushToStartTokenUpdates`, gửi lên server, và server có thể start activity bằng push khi app không chạy. Dù start bằng cách nào, user vẫn có thể tắt Live Activities trong Settings, nên kiểm tra `ActivityAuthorizationInfo().areActivitiesEnabled` và luôn có kênh dự phòng (notification thường).

## Bài tập

Thiết kế một Live Activity cho đơn giao đồ ăn: hiển thị ETA và trạng thái trên Lock Screen, cập nhật khi đơn hàng tiến triển, mà không cần app phải mở. Nêu rõ hình dạng `ContentState`, update đến từ lịch local hay push server, cách xử lý khi đơn hàng bị hủy sau khi activity đã bắt đầu, và widget hiển thị gì nếu backend ngừng gửi update trong 30 phút.
