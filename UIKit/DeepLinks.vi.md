[English](./DeepLinks.md) | [Tiếng Việt](./DeepLinks.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# Deep Link, Universal Link, và Notification Flow

## Ý chính

Các entry point từ bên ngoài nên được map vào app route một cách ổn định, kể cả khi app vừa cold launch, đang ở background, hay đang nằm trong một flow khác.

## Cần ôn

- URL parsing và route modeling: đổi URL (custom scheme như `myapp://` hoặc universal link `https://`) thành một enum `Route` có kiểu rõ ràng, để phần còn lại của app không phải làm việc với chuỗi URL.
- Authentication gating: trước khi điều hướng, kiểm tra route đó có cần đăng nhập hay quyền gì không.
- Hoãn navigation tới khi app state sẵn sàng: lúc cold launch, UI, session và dữ liệu có thể chưa sẵn sàng, nên route phải được giữ lại và chỉ thực hiện khi app báo đã sẵn sàng.
- Push notification như một navigation intent: cú tap vào notification cũng là một entry point từ bên ngoài, nên payload `userInfo` nên đi qua cùng parser và router với URL.

## Câu hỏi thực hành

- Điều gì xảy ra nếu deep link đến trước khi login xong?
- Route parsing nên nằm ở đâu?

## Câu hỏi luyện tập

- Chuyện gì xảy ra nếu deep link đến trước khi login hoàn tất?
- Việc parse route nên nằm ở đâu?

## Góc nhìn senior

Xử lý deep link là bài toán điều phối cấp app. Câu trả lời tốt nên nói về route modeling, readiness check, fallback behavior, và analytics, không chỉ là mở thẳng một screen.

## Đáp án câu hỏi luyện tập

### Chuyện gì xảy ra nếu deep link đến trước khi login hoàn tất?

App nên giữ deep link lại như một "route đang chờ", cho user đăng nhập xong, rồi mới điều hướng tới đó. Hai cách làm sai phổ biến là bỏ qua link (user bấm link mà không thấy gì) và mở thẳng màn hình cần đăng nhập (lộ dữ liệu hoặc crash vì chưa có session).

Luồng hợp lý:

1. Parser đổi URL `myapp://orders/123` thành `Route.orderDetail(id: "123")`.
2. Router cấp app kiểm tra: route này có cần đăng nhập không, session đã sẵn sàng chưa.
3. Nếu chưa, lưu `pendingRoute` và hiện màn hình login.
4. Khi login thành công, router lấy `pendingRoute`, kiểm tra lại (user này có quyền xem order 123 không), rồi điều hướng và xóa `pendingRoute`.

Cần xử lý thêm vài trường hợp biên:

- User hủy login: bỏ route, đưa về màn hình mặc định.
- User đăng nhập bằng tài khoản khác: order có thể không thuộc về họ, cần màn hình fallback kiểu "Không tìm thấy đơn hàng".
- Route chờ quá lâu, ví dụ user để app ở màn hình login cả ngày: nên có thời hạn.

Chữ "trước khi login hoàn tất" cũng bao gồm lúc cold launch, khi app còn đang khôi phục session từ Keychain. Router phải đợi tín hiệu "app đã sẵn sàng" chứ không chỉ kiểm tra đã login chưa. Trade-off: chỉ nên giữ một pending route duy nhất. Nếu có link mới đến thì thay link cũ, xếp hàng nhiều link sẽ gây điều hướng khó hiểu.

### Việc parse route nên nằm ở đâu?

Việc parse nên nằm trong một thành phần riêng, thuần logic, chỉ làm một việc: đổi đầu vào bên ngoài (URL, universal link, payload push, shortcut item) thành một enum `Route`. Nó không nên nằm trong SceneDelegate hay view controller.

```swift
enum Route: Equatable {
    case orderDetail(id: String)
    case settings
}

struct DeepLinkParser {
    func route(from url: URL) -> Route? {
        let parts: [String]
        switch url.scheme {
        case "myapp":
            // myapp://orders/123: host là "orders", path là "/123"
            parts = [url.host ?? ""] + url.pathComponents.dropFirst()
        case "https" where url.host == "example.com":
            // https://example.com/orders/123: path là "/orders/123"
            parts = Array(url.pathComponents.dropFirst())
        default:
            return nil // scheme hoặc domain lạ: bỏ qua
        }

        switch parts {
        case ["settings"]:
            return .settings
        case let p where p.count == 2 && p[0] == "orders" && !p[1].isEmpty:
            return .orderDetail(id: p[1]) // id vẫn phải được kiểm tra lại ở tầng dữ liệu
        default:
            return nil
        }
    }
}
```

Ví dụ này xử lý được cả `myapp://orders/123` (host là `orders`) lẫn `https://example.com/orders/123` (path là `/orders/123`), nên hai kiểu link cùng ra một `Route`. Nó cũng kiểm tra scheme và domain, và trả về `nil` cho mọi URL không nhận ra để router hiện màn hình mặc định thay vì crash. Lợi ích:

- Test bằng unit test đơn giản, không cần chạy UI.
- Custom scheme, universal link và push dùng chung một chỗ, không bị lệch logic.
- SceneDelegate chỉ chuyển tiếp dữ liệu, router hoặc coordinator chỉ lo điều hướng. Mỗi bên có một trách nhiệm rõ.

Parser cũng là chỗ để validate, vì URL là dữ liệu từ bên ngoài và không đáng tin. Trade-off: với app nhỏ vài route, một hàm `switch` là đủ, không cần framework routing phức tạp.

## Bẫy phỏng vấn

### "Cold launch từ một URL, code trong scene(_:openURLContexts:) có chạy không?"

**Dễ trả lời sai:** Có, mọi URL đều đi qua `scene(_:openURLContexts:)`.

**Nên trả lời:** Method đó chỉ chạy khi scene đã tồn tại, tức là app đang chạy hoặc ở background. Khi cold launch, URL nằm trong `connectionOptions.urlContexts` của `scene(_:willConnectTo:options:)`, còn universal link thì nằm trong `connectionOptions.userActivities`. Khi app đang chạy, universal link đi qua `scene(_:continue:)`. Nếu chỉ xử lý một chỗ, link sẽ "không có tác dụng" đúng vào trường hợp quan trọng nhất là lần đầu mở app.

### "Universal link đã cấu hình xong, sao bấm vào vẫn mở Safari?"

**Dễ trả lời sai:** Do file AASA sai, sửa file trên server là hết ngay.

**Nên trả lời:** Có nhiều nguyên nhân hợp lệ. Link được gõ trực tiếp vào thanh địa chỉ Safari sẽ không mở app. Bấm link trên chính domain đó trong Safari cũng thường không mở app. User từng chọn "Mở trong Safari" thì iOS nhớ lựa chọn đó. Ngoài ra, từ iOS 14 thiết bị không lấy file `apple-app-site-association` trực tiếp từ server của bạn mà qua CDN của Apple, chủ yếu lúc cài hoặc cập nhật app, không phải mỗi lần bấm link. CDN còn cache file, nên sửa file trên server không có hiệu lực ngay. Khi debug có thể thêm `?mode=developer` vào associated domain (ví dụ `applinks:example.com?mode=developer`) để thiết bị lấy file thẳng từ server; cách này cần bật Associated Domains Development trong phần Developer của Settings và chỉ áp dụng cho build development.

### "Deep link chứa action, ví dụ myapp://pay?amount=100, xử lý thẳng có được không?"

**Dễ trả lời sai:** Được, URL do app mình định nghĩa nên cứ tin và thực hiện.

**Nên trả lời:** Custom URL scheme không có cơ chế sở hữu, bất kỳ app hay trang web nào cũng có thể gọi `myapp://` với tham số tùy ý. Deep link chỉ nên đưa user tới màn hình, không bao giờ tự thực hiện hành động có side effect như thanh toán, xóa dữ liệu hay đổi cài đặt. Hãy validate mọi tham số, và yêu cầu user xác nhận trong app. Universal link an toàn hơn về nguồn gốc vì gắn với domain, nhưng tham số của nó vẫn là input không đáng tin.

## Bài tập

Thiết kế routing cho `myapp://orders/123` và một universal link tới cùng order đó. Giải thích app sẽ hoạt động thế nào khi cold launch, khi đang ở tab khác, và khi user chưa đăng nhập.
