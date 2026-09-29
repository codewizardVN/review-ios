[English](./Coordinator.md) | [Tiếng Việt](./Coordinator.vi.md)

[← Architecture](./README.vi.md)

# Coordinator Pattern

## Ý chính

Coordinator tách navigation và flow orchestration ra khỏi view controller hoặc view, để screen tập trung vào render UI và xử lý user interaction.

## Vấn đề nó giải quyết

- Giảm navigation logic bên trong `UIViewController` hoặc `ViewModel`
- Làm flow dễ test và dễ lý giải hơn
- Tập trung hóa việc xử lý deep link và ownership của child flow

## Ví dụ

```swift
@MainActor
protocol AppCoordinating {
    func showLogin()
    func showHome()
}

@MainActor
final class AppCoordinator: AppCoordinating {
    private let navigationController: UINavigationController

    init(navigationController: UINavigationController) {
        self.navigationController = navigationController
    }

    func showLogin() {
        let controller = LoginViewController()
        controller.onLoginSuccess = { [weak self] in
            self?.showHome()
        }
        navigationController.setViewControllers([controller], animated: false)
    }

    func showHome() {
        navigationController.pushViewController(HomeViewController(), animated: true)
    }
}
```

`@MainActor` là cần thiết: `UINavigationController` và mọi view controller đều bị isolate vào main actor, nên trong Swift 6 language mode một coordinator không đánh dấu `@MainActor` sẽ bị compiler báo lỗi khi gọi `setViewControllers` hay tạo `LoginViewController()`. (Nếu target bật default actor isolation là `MainActor` của Swift 6.2, mặc định của project app mới tạo bằng Xcode 26, thì annotation này được suy ra sẵn.)

## Câu hỏi thực hành

- Khi nào Coordinator hữu ích, và khi nào là over-engineering?
- Có nên để quyết định navigation trong ViewModel không?

## Câu hỏi luyện tập

- Khi nào Coordinator hữu ích, và khi nào nó là over-engineering?
- Quyết định navigation có nên nằm trong ViewModel không?

## Góc nhìn senior

Coordinator hữu ích khi flow bắt đầu phức tạp, có nhiều child journey, hoặc phải phản ứng với event cấp app như authentication và deep link. Với app rất nhỏ, cách đơn giản hơn có thể đã đủ.

## Đáp án câu hỏi luyện tập

### Khi nào Coordinator hữu ích, và khi nào nó là over-engineering?

Coordinator hữu ích khi navigation không còn là "màn A mở màn B" mà là một flow có nhiều nhánh, nhiều điểm vào, hoặc phải phản ứng với sự kiện cấp app.

Các tình huống đáng dùng:

- Flow nhiều bước như onboarding, checkout, đăng ký có xác thực OTP.
- Cùng một màn hình được dùng trong nhiều flow: `LoginViewController` mở từ splash và cũng mở giữa checkout, sau khi login xong mỗi nơi đi tiếp một kiểu khác nhau.
- Deep link hoặc push notification cần dựng lại cả navigation stack.
- Trạng thái đăng nhập thay đổi phải reset root, như `showLogin()` dùng `setViewControllers` trong ví dụ.

Cơ chế: coordinator giữ `UINavigationController`, tự tạo màn hình và lắng nghe event (như closure `onLoginSuccess`). Màn hình không biết màn tiếp theo là gì, nên tái sử dụng được và dễ test.

Nó là over-engineering khi app chỉ có vài màn hình đi thẳng một chiều, hoặc khi mỗi màn hình có một coordinator kèm protocol chỉ để gọi một lệnh push. Với SwiftUI, `NavigationStack(path:)` và `navigationDestination(for:)` đã cho phép gom navigation vào một mảng dữ liệu; một router object nhỏ giữ `path` thường đã đủ. Chi phí phải nhớ: quản lý vòng đời child coordinator và xử lý nút Back của hệ thống.

### Quyết định navigation có nên nằm trong ViewModel không?

ViewModel nên quyết định "chuyện gì vừa xảy ra" hoặc "người dùng muốn đi đâu", nhưng không nên quyết định "đi bằng cách nào".

Cụ thể: ViewModel có thể phát ra một event như `.loginSucceeded`, `.needsTwoFactor` hoặc `.forgotPasswordTapped` qua closure hay một `enum Route`. Coordinator hoặc router nhận event đó và dịch thành hành động UIKit/SwiftUI thật: push, present, đổi root. Nhờ vậy ViewModel không import UIKit, không giữ tham chiếu tới view controller, và test chỉ cần kiểm tra ViewModel phát đúng route:

```swift
var routes: [LoginRoute] = []
vm.onRoute = { routes.append($0) }
vm.forgotPasswordTapped()
XCTAssertEqual(routes, [.forgotPassword])
```

Những quyết định mang tính nghiệp vụ, như "tài khoản chưa xác minh thì phải qua màn xác minh", có thể nằm trong ViewModel hoặc coordinator, miễn là nó được biểu diễn bằng dữ liệu. Trong SwiftUI, ViewModel sửa một mảng `path` gồm các giá trị enum là chấp nhận được vì đó vẫn là dữ liệu thuần, test được. Điều cần tránh là ViewModel tự tạo `ForgotPasswordViewController` rồi gọi `navigationController?.pushViewController`.

## Bẫy phỏng vấn

### "Tạo child coordinator rồi gọi `start()` là xong?"

**Dễ trả lời sai:** Viết `let child = ForgotPasswordCoordinator(navigationController: nav); child.start()` trong một hàm, rồi ngạc nhiên vì callback không bao giờ chạy.

**Nên trả lời:** Không ai giữ strong reference tới `child`, nên nó bị giải phóng ngay khi hàm kết thúc; các closure `[weak self]` bên trong trả về `nil` và không làm gì. Parent phải giữ child trong một mảng như `childCoordinators` và xoá nó khi flow kết thúc. Ngược lại, quên xoá thì child bị leak mãi.

### "Người dùng bấm nút Back hệ thống hoặc vuốt để quay lại, coordinator có biết không?"

**Dễ trả lời sai:** "Có, coordinator luôn biết vì nó quản lý navigation."

**Nên trả lời:** Nút Back và cử chỉ vuốt pop view controller trực tiếp trên `UINavigationController`, bỏ qua coordinator hoàn toàn. Nếu không xử lý, child coordinator vẫn nằm trong mảng dù màn hình đã biến mất. Cách phổ biến là làm `UINavigationControllerDelegate` và trong `navigationController(_:didShow:animated:)` lấy view controller vừa rời màn hình qua `navigationController.transitionCoordinator?.viewController(forKey: .from)`. Nếu nó không còn nằm trong `navigationController.viewControllers` thì đó là pop (không phải push một màn mới), và bạn xoá child coordinator tương ứng. Làm ở `didShow` để không xử lý nhầm khi người dùng vuốt dở rồi huỷ.

### "Object nào nên sở hữu `AppCoordinator`?"

**Dễ trả lời sai:** "View controller gốc giữ coordinator", hoặc "coordinator tự giữ chính nó qua singleton".

**Nên trả lời:** Root coordinator nên được `SceneDelegate` (hoặc `App` trong SwiftUI) sở hữu, vì nó sống bằng vòng đời của scene. Coordinator giữ navigation controller, navigation controller giữ các màn hình; màn hình chỉ tham chiếu ngược lại qua closure `[weak self]` như `onLoginSuccess`. Nếu closure capture `self` mạnh, bạn có vòng coordinator → navigation controller → controller → closure → coordinator, tức retain cycle.

## Bài tập

Lấy một login flow đang `push` sang `ForgotPasswordViewController` trực tiếp từ `LoginViewController`. Chuyển trách nhiệm đó sang coordinator. Sau đó giải thích object nào nên sở hữu coordinator và vì sao.
