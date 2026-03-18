[English](./Coordinator.md) | [Tiếng Việt](./Coordinator.vi.md)

[← Architecture](./README.md)

# Coordinator Pattern

## Key Idea

Coordinator moves navigation and flow orchestration out of view controllers or views, so screens focus on rendering and user interaction.

## What Problems It Solves

- Reduces navigation logic inside `UIViewController` or `ViewModel`
- Makes flows easier to test and reason about
- Centralizes deep link handling and child-flow ownership

## Example

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

## Practice Questions

- When is Coordinator helpful, and when is it over-engineering?
- Should navigation decisions live in the ViewModel?

## Senior Take

Coordinator is useful when flows become complex, have multiple child journeys, or must react to app-level events like authentication and deep links. For a very small app, a simpler approach may be enough.

## Exercise

Take a login flow that pushes `ForgotPasswordViewController` directly from `LoginViewController`. Move that responsibility into a coordinator. Then explain which object should own the coordinator and why.
