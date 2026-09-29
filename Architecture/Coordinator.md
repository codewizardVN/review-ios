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

`@MainActor` is required: `UINavigationController` and every view controller are isolated to the main actor, so in the Swift 6 language mode a coordinator that isn't marked `@MainActor` gets compiler errors when it calls `setViewControllers` or creates `LoginViewController()`. (If the target uses Swift 6.2's default actor isolation of `MainActor`, the default for new app projects created with Xcode 26, this annotation is inferred for you.)

## Practice Questions

- When is Coordinator helpful, and when is it over-engineering?
- Should navigation decisions live in the ViewModel?

## Senior Take

Coordinator is useful when flows become complex, have multiple child journeys, or must react to app-level events like authentication and deep links. For a very small app, a simpler approach may be enough.

## Practice Question Answers

### When is Coordinator helpful, and when is it over-engineering?

Coordinator is helpful when navigation is no longer "screen A opens screen B" but a flow with several branches, several entry points, or one that must react to app-level events.

Situations where it pays off:

- Multi-step flows such as onboarding, checkout, or sign-up with OTP verification.
- The same screen used in several flows: `LoginViewController` opened from the splash screen and also mid-checkout, with each place continuing differently after login.
- Deep links or push notifications that need to rebuild the whole navigation stack.
- Login state changes that must reset the root, like `showLogin()` using `setViewControllers` in the example.

Mechanism: the coordinator holds the `UINavigationController`, creates screens itself, and listens for events (like the `onLoginSuccess` closure). A screen doesn't know what comes next, so it is reusable and easy to test.

It is over-engineering when the app has only a few screens going one way, or when every screen gets a coordinator plus a protocol just to perform one push. In SwiftUI, `NavigationStack(path:)` and `navigationDestination(for:)` already let you centralize navigation in an array of data; a small router object holding the `path` is often enough. Costs to remember: managing child coordinator lifetimes and handling the system Back button.

### Should navigation decisions live in the ViewModel?

The ViewModel should decide "what just happened" or "where the user wants to go", but not "how to get there".

Concretely: the ViewModel can emit an event such as `.loginSucceeded`, `.needsTwoFactor`, or `.forgotPasswordTapped` through a closure or an `enum Route`. The coordinator or router receives that event and translates it into a real UIKit/SwiftUI action: push, present, change root. That way the ViewModel doesn't import UIKit, holds no reference to view controllers, and the test only checks that the ViewModel emitted the right route:

```swift
var routes: [LoginRoute] = []
vm.onRoute = { routes.append($0) }
vm.forgotPasswordTapped()
XCTAssertEqual(routes, [.forgotPassword])
```

Business-flavoured decisions, like "an unverified account must go through the verification screen", can live in the ViewModel or the coordinator, as long as they are expressed as data. In SwiftUI, a ViewModel mutating a `path` array of enum values is acceptable because it is still plain, testable data. What to avoid is the ViewModel creating a `ForgotPasswordViewController` and calling `navigationController?.pushViewController` itself.

## Interview Traps

### "Create a child coordinator, call `start()`, and you're done?"

**Common wrong answer:** Writing `let child = ForgotPasswordCoordinator(navigationController: nav); child.start()` inside a function, then being surprised that callbacks never fire.

**Better answer:** Nothing holds a strong reference to `child`, so it is deallocated as soon as the function returns; the `[weak self]` closures inside find `nil` and do nothing. The parent must keep the child in an array such as `childCoordinators` and remove it when the flow finishes. Conversely, forgetting to remove it leaks the child forever.

### "When the user taps the system Back button or swipes back, does the coordinator know?"

**Common wrong answer:** "Yes, the coordinator always knows because it manages navigation."

**Better answer:** The Back button and swipe gesture pop the view controller directly on the `UINavigationController`, bypassing the coordinator entirely. If you don't handle it, the child coordinator stays in the array even though its screen is gone. A common fix is to act as `UINavigationControllerDelegate` and, in `navigationController(_:didShow:animated:)`, get the view controller that just left the screen via `navigationController.transitionCoordinator?.viewController(forKey: .from)`. If it is no longer in `navigationController.viewControllers`, it was a pop (not a push of a new screen), and you remove the matching child coordinator. Doing it in `didShow` avoids mishandling a swipe the user starts and then cancels.

### "Which object should own the `AppCoordinator`?"

**Common wrong answer:** "The root view controller holds the coordinator," or "the coordinator keeps itself alive as a singleton."

**Better answer:** The root coordinator should be owned by the `SceneDelegate` (or the `App` in SwiftUI), because it lives for the scene's lifetime. The coordinator holds the navigation controller, the navigation controller holds the screens; screens only refer back through `[weak self]` closures like `onLoginSuccess`. If the closure captures `self` strongly, you get the loop coordinator → navigation controller → controller → closure → coordinator, which is a retain cycle.

## Exercise

Take a login flow that pushes `ForgotPasswordViewController` directly from `LoginViewController`. Move that responsibility into a coordinator. Then explain which object should own the coordinator and why.
