[English](./UITests.md) | [Tiếng Việt](./UITests.vi.md)

[← Testing](./README.vi.md)

# UI Tests

## Ý chính

UI test xác nhận các user flow quan trọng từ đầu đến cuối. Nó tạo độ tin cậy rằng screen, navigation, và các integration point vẫn hoạt động sau thay đổi.

## Cần ôn

- Chỉ dùng UI test cho high-value flow, không phải mọi permutation: UI test chậm và dễ flaky, nên dành cho vài journey quan trọng; các biến thể (sai email, lỗi server...) để unit test lo.
- Ưu tiên accessibility identifier ổn định: tìm element bằng `accessibilityIdentifier` (ví dụ `login.email`) thay vì text hiển thị, vì text đổi theo ngôn ngữ và nội dung.
- Giữ setup có tính xác định bằng launch arguments và dữ liệu stub: test truyền cờ qua `launchArguments`/`launchEnvironment`, app đọc cờ đó lúc khởi động để dùng dữ liệu giả thay vì backend thật, nên mỗi lần chạy cho cùng kết quả.
- Tránh phụ thuộc vào timing mong manh: không dùng `sleep` cố định; chờ theo điều kiện bằng `waitForExistence(timeout:)` hoặc expectation.
- UI test chạy trong một process riêng và điều khiển app qua accessibility (XCUITest), nên không truy cập trực tiếp được object trong app.

## Ví dụ

```swift
// Từ Xcode 16, XCUIApplication/XCUIElement là @MainActor, nên test method
// (hoặc cả class) cần @MainActor để compile ở Swift 6 language mode.
@MainActor
func test_login_success_showsHomeScreen() {
    let app = XCUIApplication()
    app.launchArguments = ["-ui-test-login-success"]
    app.launch()

    app.textFields["login.email"].tap()
    app.textFields["login.email"].typeText("hello@example.com")
    app.secureTextFields["login.password"].tap()
    app.secureTextFields["login.password"].typeText("123456")
    app.buttons["login.submit"].tap()

    XCTAssertTrue(app.staticTexts["home.title"].waitForExistence(timeout: 2))
}
```

## Câu hỏi thực hành

- Những flow nào nên được bảo vệ bằng UI test trước?
- Làm sao giảm flaky UI tests?

## Câu hỏi luyện tập

- Flow nào xứng đáng có UI test trước tiên?
- Làm sao bạn giảm tình trạng UI test bị flaky?

## Góc nhìn senior

UI test có chi phí cao. Hãy dùng chúng để bảo vệ một vài journey thật sự quan trọng cho business như login, checkout, onboarding, hoặc migration rủi ro. Mục tiêu là confidence per cost, không phải phủ test bằng mọi giá.

## Đáp án câu hỏi luyện tập

### Flow nào xứng đáng có UI test trước tiên?

Ưu tiên những flow mà nếu hỏng thì app mất tiền, mất user hoặc user bị kẹt: thường là login, onboarding lần đầu, checkout/thanh toán, và các flow chạy sau migration dữ liệu rủi ro.

Cách chọn: nhân "mức thiệt hại khi hỏng" với "khả năng hỏng mà unit test không bắt được". UI test mạnh nhất ở chỗ nó kiểm tra các mảnh ghép *nối với nhau*: navigation, deep link, màn hình được push đúng, keyboard, permission alert, dữ liệu đi xuyên nhiều màn hình. Những thứ này unit test của từng ViewModel không thấy được.

Một flow tốt để test đầu tiên thường giống ví dụ `test_login_success_showsHomeScreen`: một happy path ngắn, đi từ màn hình đầu đến kết quả mà user quan tâm, và assert một điều có ý nghĩa (màn hình Home xuất hiện).

Không nên dùng UI test cho mọi permutation: sai định dạng email, mật khẩu ngắn, mười loại lỗi server. Các nhánh đó thuộc về unit test của `LoginViewModel`, nhanh và ổn định hơn nhiều. UI test chậm (vài giây đến vài chục giây mỗi test), tốn thời gian CI và dễ flaky, nên mỗi test phải "đáng tiền". Một bộ nhỏ 5–15 UI test cho các journey chính thường mang lại nhiều confidence hơn 200 test phủ mọi màn hình.

### Làm sao bạn giảm tình trạng UI test bị flaky?

Giảm flaky bằng cách loại bỏ mọi thứ không xác định: dữ liệu, thời gian, trạng thái cũ và cách tìm element.

- **Dữ liệu cố định**: truyền `launchArguments` hoặc `launchEnvironment` (như `-ui-test-login-success`) để app dùng stub server hoặc dữ liệu local thay cho backend thật. Network thật là nguồn flaky số một.
- **Chờ theo điều kiện, không theo thời gian**: dùng `waitForExistence(timeout:)` hoặc `XCTNSPredicateExpectation` thay vì `sleep`. Test chờ đúng đến khi element xuất hiện, không lâu hơn.
- **Trạng thái sạch**: mỗi test tự launch app với state reset để không phụ thuộc test trước. Test runner không xoá được dữ liệu bên trong app, nên cách thường làm là truyền một cờ (ví dụ `-reset-state`) và để app, khi thấy cờ này, tự xoá keychain, dùng một `UserDefaults(suiteName:)` riêng cho test và database tạm.
- **Selector ổn định**: dùng `accessibilityIdentifier` như `login.email`, không dùng text hiển thị vốn đổi theo ngôn ngữ và copy.
- **Tắt animation** khi app chạy ở chế độ UI test để giảm thời gian chờ transition, ví dụ app gọi `UIView.setAnimationsEnabled(false)` khi nhận launch argument tương ứng.
- **Xử lý system alert** (xin quyền vị trí, thông báo...): dùng `addUIInterruptionMonitor` (handler chỉ chạy khi test tương tác tiếp với app, nên sau khi alert hiện cần một thao tác như `app.tap()`), hoặc tìm alert qua `XCUIApplication(bundleIdentifier: "com.apple.springboard")`, hoặc cấp sẵn quyền cho simulator bằng `xcrun simctl privacy` trước khi chạy test.

Trade-off: stub quá nhiều làm UI test không còn phát hiện lỗi tích hợp với backend thật. Nhiều team giữ thêm một bộ nhỏ chạy với staging, tách riêng khỏi pipeline chính để flaky ở đó không chặn merge.

## Bẫy phỏng vấn

### "Test fail thỉnh thoảng vì màn hình chưa load kịp. Thêm `sleep(3)` có được không?"

**Dễ trả lời sai:** Được, chỉ cần tăng thời gian chờ đủ lớn là test sẽ ổn định.

**Nên trả lời:** `sleep` vừa chậm vừa không sửa được gốc rễ: trên máy CI bận nó vẫn có thể không đủ, còn trên máy nhanh nó lãng phí thời gian ở mọi lần chạy. Nên chờ theo điều kiện, ví dụ `XCTAssertTrue(app.staticTexts["home.title"].waitForExistence(timeout: 5))`, vì nó trả về ngay khi element xuất hiện. Nếu cần chờ element biến mất, từ Xcode 16 XCTest có `waitForNonExistence(timeout:)` (trả về `Bool`, nên bọc trong `XCTAssertTrue`); với Xcode cũ hơn thì dùng `XCTNSPredicateExpectation` với predicate `exists == false`.

### "Trong UI test, có thể inject `FakeAuthService` vào ViewModel như unit test không?"

**Dễ trả lời sai:** Có, chỉ cần `@testable import` app rồi gán fake vào ViewModel trước khi tap.

**Nên trả lời:** Không. UI test chạy ở một process riêng (test runner) và điều khiển app qua accessibility, nên nó không truy cập được object bên trong app, kể cả khi có `@testable import`. Cách đúng là truyền tín hiệu qua `launchArguments`/`launchEnvironment`; app đọc `ProcessInfo.processInfo.arguments` lúc khởi động và tự chọn dependency fake. Nên đặt đoạn code này sau `#if DEBUG` để nó không vào bản release.

### "Tìm button bằng `app.buttons["Đăng nhập"]` có vấn đề gì không?"

**Dễ trả lời sai:** Không sao, dùng text hiển thị dễ đọc và giống cách user nhìn màn hình.

**Nên trả lời:** Text hiển thị thay đổi theo localization, theo chỉnh sửa copy, và có thể bị trùng giữa nhiều element, nên test sẽ vỡ dù hành vi không đổi. Nên gán `accessibilityIdentifier` ổn định như `login.submit`; identifier không được VoiceOver đọc nên không ảnh hưởng người dùng. Không nên gán identifier vào `accessibilityLabel`, vì label là thứ VoiceOver đọc cho user và phải là câu tự nhiên.

## Bài tập

Chọn một flow thật sự quan trọng trong app của bạn. Xác định launch setup, accessibility identifier cần có, và các assertion đủ ý nghĩa mà không buộc test phải bám quá chặt vào chi tiết UI.
