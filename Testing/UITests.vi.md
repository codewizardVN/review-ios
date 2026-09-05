[English](./UITests.md) | [Tiếng Việt](./UITests.vi.md)

[← Testing](./README.vi.md)

# UI Tests

## Ý chính

UI test xác nhận các user flow quan trọng từ đầu đến cuối. Nó tạo độ tin cậy rằng screen, navigation, và các integration point vẫn hoạt động sau thay đổi.

## Cần ôn

- Chỉ dùng UI test cho high-value flow, không phải mọi permutation
- Ưu tiên accessibility identifier ổn định
- Giữ setup có tính xác định bằng launch arguments và dữ liệu stub
- Tránh phụ thuộc vào timing mong manh

## Ví dụ

```swift
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

## Bài tập

Chọn một flow thật sự quan trọng trong app của bạn. Xác định launch setup, accessibility identifier cần có, và các assertion đủ ý nghĩa mà không buộc test phải bám quá chặt vào chi tiết UI.
