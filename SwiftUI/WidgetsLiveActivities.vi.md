[English](./WidgetsLiveActivities.md) | [Tiếng Việt](./WidgetsLiveActivities.vi.md)

[← SwiftUI](./README.vi.md)

# Widgets và Live Activities

## Ý chính

Một widget extension là một process riêng biệt với bộ nhớ và ngân sách thực thi của chính nó — nó render một snapshot của state theo timeline do hệ thống kiểm soát, không phải view sống động của app đang chạy. Live Activities mở rộng model đó cho state cập nhật real-time, thường xuyên trên Lock Screen và Dynamic Island.

## Những điều cần nắm

- `TimelineProvider` / `AppIntentTimelineProvider` — cung cấp danh sách giá trị `TimelineEntry` kèm ngày; hệ thống render entry nào có ngày đã qua, theo lịch của riêng nó, không phải của bạn
- Widget family (`systemSmall/Medium/Large`, `accessoryCircular/Rectangular/Inline`) — layout phải thích ứng theo từng family, và accessory widget trên Lock Screen render ở chế độ tint, monochrome
- Chia sẻ dữ liệu — widget extension không thể truy cập in-memory state của app chính; dữ liệu phải đi qua App Group container (shared `UserDefaults`, file, hoặc SQLite/Core Data)
- `WidgetCenter.shared.reloadTimelines(ofKind:)` — cách app chính request widget refresh thay vì phụ thuộc vào timeline riêng của widget (chịu ràng buộc ngân sách reload toàn hệ thống)
- ActivityKit / Live Activities — `Activity<Attributes>`, `ContentState` cập nhật thường xuyên so với attribute tĩnh, khởi động từ app, cập nhật qua push (payload `content-state`) hoặc local với ngân sách giới hạn
- Vùng layout Dynamic Island — compact leading/trailing, minimal, expanded — mỗi vùng cần view riêng, và nội dung expanded vẫn phải giữ nhẹ
- Xử lý kết thúc vòng đời — một Live Activity mặc định có thời lượng tối đa 8 giờ (có thể gia hạn) và phải được kết thúc tường minh, nếu không nó sẽ trở nên stale trên Lock Screen
- Deep link — widget và Live Activity mở app qua `widgetURL(_:)` hoặc `Link`, chứ không giữ tham chiếu tới state của app

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

## Bài tập

Thiết kế một Live Activity cho đơn giao đồ ăn: hiển thị ETA và trạng thái trên Lock Screen, cập nhật khi đơn hàng tiến triển, mà không cần app phải mở. Nêu rõ hình dạng `ContentState`, update đến từ lịch local hay push server, cách xử lý khi đơn hàng bị hủy sau khi activity đã bắt đầu, và widget hiển thị gì nếu backend ngừng gửi update trong 30 phút.
