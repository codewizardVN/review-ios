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
protocol AppCoordinating {
    func showLogin()
    func showHome()
}

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

## Câu hỏi thực hành

- Khi nào Coordinator hữu ích, và khi nào là over-engineering?
- Có nên để quyết định navigation trong ViewModel không?

## Góc nhìn senior

Coordinator hữu ích khi flow bắt đầu phức tạp, có nhiều child journey, hoặc phải phản ứng với event cấp app như authentication và deep link. Với app rất nhỏ, cách đơn giản hơn có thể đã đủ.

## Bài tập

Lấy một login flow đang `push` sang `ForgotPasswordViewController` trực tiếp từ `LoginViewController`. Chuyển trách nhiệm đó sang coordinator. Sau đó giải thích object nào nên sở hữu coordinator và vì sao.
