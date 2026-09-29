[English](./Coordinator.md) | [Tiếng Việt](./Coordinator.vi.md)

[← UIKit and App Lifecycle](./README.md)

# Coordinator and Router

## Key Idea

Navigation is application flow, not view rendering. Coordinator or router patterns keep screens from owning too much knowledge about the rest of the app.

## What To Review

- Root coordinator vs child coordinator: the root (often called `AppCoordinator`) is created by the SceneDelegate, owns the window or root view controller, and decides the big flows (onboarding, login, main tabs). A child coordinator owns a sub-flow (checkout, auth), is created and held by its parent, and reports back to the parent when the flow finishes.
- How screens communicate navigation intent upward: a screen does not create the next screen itself; it calls a closure or delegate like "the user wants to check out", and the coordinator receives that intent and decides where to go.
- Deep links entering existing flows: the deep link is turned into a route and passed from the root down through the child coordinators, each level handling its own part (see the answer below).
- Ownership and lifetime of coordinators: who holds the strong reference to a coordinator, when it is released, and how to avoid retain cycles between the coordinator, the navigation controller, and the view controllers.

## Practice Questions

- When should a screen trigger navigation directly?
- Who should respond to a deep link that opens a nested flow?

## Senior Take

Coordinator patterns are useful when navigation complexity is real. If there is only one simple flow, adding layers may not pay off. The key is matching indirection to product complexity.

## Practice Question Answers

### When should a screen trigger navigation directly?

A screen should navigate on its own when the destination is "internal" to it: not reused in another flow, not dependent on app state, and nobody else needs to know. Examples: presenting a `UIAlertController`, an image picker, a `UIActivityViewController` for sharing, or a small detail screen that belongs only to that feature. In these cases forcing the screen to send an intent up to a coordinator only adds code with no benefit.

A screen should not navigate on its own when:

- The destination belongs to another feature. The screen would have to import and create another module's view controller, which tangles dependencies.
- The next step depends on context. For example, the cart screen goes to shipping or to login depending on whether the user is signed in.
- The same screen is used in several flows, and each flow wants to continue differently.
- You need deep links that jump straight into the middle of the flow.

Then the screen should only report intent, for example an `onCheckoutTapped` closure or a `cartDidRequestCheckout()` delegate call, and the coordinator decides where to go. Trade-off: indirection makes screens easier to test and reuse, but every added layer is another place to read while debugging. Start simple and only extract navigation when one of the reasons above really applies.

### Who should respond to a deep link that opens a nested flow?

The app-level coordinator should receive the deep link first, then forward it down to the coordinator that owns the target flow. Screens should not handle it themselves. The reason is that only the top level has enough context: whether the user is signed in, which tab is active, whether a modal is open and needs to be closed.

A sensible flow usually looks like this:

1. The SceneDelegate receives the URL and hands it to a parser that turns it into a `Route`, for example `.checkout(.payment)`.
2. `AppCoordinator` checks preconditions (login, required data), dismisses any open modal, and selects the right tab.
3. `AppCoordinator` creates or reuses a `CheckoutCoordinator` and calls `checkoutCoordinator.handle(.payment)`.
4. `CheckoutCoordinator` is the only one that knows the order cart, shipping, payment. It builds the navigation stack correctly itself, for example pushing cart and shipping underneath so the back button still makes sense.

Each coordinator only understands its part of the route and passes the rest down to its child, like a chain of responsibility. Trade-off: if the flow is not ready (a missing shipping address, say), the child coordinator needs a fallback, such as stopping at the shipping step instead of jumping straight to payment.

## Interview Traps

### "When the user taps the system back button, is the child coordinator released?"

**Common wrong answer:** Yes, when the view controller is popped, the coordinator goes away too.

**Better answer:** The parent usually keeps children in a `childCoordinators` array. The back button and the swipe-back gesture are handled by `UINavigationController`, and the coordinator is not told. So the child coordinator stays in the array, leaking and sometimes handling stale events. You need to listen to `navigationController(_:didShow:animated:)` from `UINavigationControllerDelegate`, get the view controller that just left the screen via `navigationController.transitionCoordinator?.viewController(forKey: .from)`, check that it is no longer in `navigationController.viewControllers` (meaning it was popped, not covered by a push), and then call `childDidFinish` for the child coordinator that owns that screen.

### "The view controller holds the coordinator, the coordinator holds the navigation controller. Any problem?"

**Common wrong answer:** No problem, just let the view controller keep a strong reference to the coordinator so it can call navigation conveniently.

**Better answer:** The coordinator holds the navigation controller, the navigation controller holds the view controller, and if the view controller strongly holds the coordinator you have a retain cycle and the whole flow is never released. The view controller should hold the coordinator through `weak var coordinator`, or better, only receive a closure like `var onFinish: (() -> Void)?` that the coordinator assigns with `[weak self]`. The closure approach also means the view controller does not need to know the coordinator's type.

### "Should every UIKit app use Coordinators?"

**Common wrong answer:** Yes, Coordinator is best practice, and every screen should have its own coordinator.

**Better answer:** Coordinators solve complex navigation: many flows, reused flows, deep links, login conditions. For an app with a few screens, one coordinator per screen just adds boilerplate and makes debugging harder. The senior answer is to split coordinators by flow (auth, checkout, onboarding), not by screen, and to explain which concrete problem made you choose them.

## Exercise

Take a checkout flow with cart, shipping, payment, and confirmation screens. Sketch a root coordinator plus one child coordinator. Then explain where deep link handling should enter that flow.
