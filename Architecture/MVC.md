[English](./MVC.md) | [Tiếng Việt](./MVC.vi.md)

[← Architecture](./README.md)

# MVC (Model-View-Controller)

## Key Idea

The default pattern in UIKit apps. The Controller mediates between the Model (data/business logic) and the View (UI).

## Strengths

- Simple to start with
- Familiar to most iOS developers
- Works well for small, standalone screens

## Limitations

- Controller tends to grow ("Massive View Controller")
- Hard to unit test because controller is tightly coupled to UIKit lifecycle
- Business logic, navigation, and UI often end up in the same place

## Practice Questions

- After splitting a ProductListViewController's URLSession call, inline price formatting, and detail-screen push into Model, Controller, and a separate Service, what becomes unit-testable and what remains untestable in UIKit MVC regardless?

## Senior Take

MVC is not inherently broken — it is often misapplied. A disciplined MVC with thin controllers, separate model layer, and extracted services can be maintainable. The real problem is that UIKit makes it easy to dump everything into the controller.

## Practice Question Answers

### After splitting a ProductListViewController's URLSession call, inline price formatting, and detail-screen push into Model, Controller, and a separate Service, what becomes unit-testable and what remains untestable in UIKit MVC regardless?

Everything that no longer depends on UIKit becomes testable: the Service that fetches data, the price formatting logic, and the mapping of data into Models. What stays hard to test is whatever remains in the Controller: pushing the detail screen, configuring the table view/cells, and the lifecycle that triggers loading.

After the split, `ProductListViewController` only calls a `ProductService` (a protocol, e.g. `func fetchProducts() async throws -> [Product]`). In tests you inject a fake service that returns fixed data, or you test the real implementation with a `URLProtocol` stub so no network call happens. Price formatting becomes a pure function such as `PriceFormatter.format(_ price: Decimal, locale: Locale) -> String`: pass a fixed `Locale` in the test and the result no longer depends on the machine's settings. Models and JSON decoding are testable like any other Swift code.

The rest is still tied to UIKit:

- Pushing the detail screen needs a real `UINavigationController`: you embed the controller in a navigation controller, simulate selecting a cell, then check `topViewController`. It works, but it is already an integration test with UIKit: you must push without animation (or wait for the animation to finish), and more complex transitions such as present usually need the view to be in a window.
- Loading is attached to `viewDidLoad`, so tests must call `loadViewIfNeeded()`.
- Whether cells render correctly usually needs snapshot tests or UI tests.

If you want navigation testable too, you replace the direct push with an `onSelectProduct` closure or a coordinator. At that point you have moved into MVVM/Coordinator. In plain MVC the controller is always the "glue" that can't be tested cheaply, so the goal is to keep it as thin as possible.

## Interview Traps

### "Is Apple's MVC the same as the original Smalltalk MVC?"

**Common wrong answer:** "Yes, the View observes the Model and updates itself when the Model changes." That is classic MVC, not how Cocoa works.

**Better answer:** In Cocoa MVC the Controller is a mediator: View and Model don't know about each other, and every change flows through the Controller. On top of that, `UIViewController` owns its view and its lifecycle, so in practice View and Controller are fused into one unit. That is exactly why controllers grow large and are hard to test.

### "Massive View Controller is MVC's fault, so switching to MVVM fixes it?"

**Common wrong answer:** "Yes, MVVM solves Massive View Controller." If you only move code from the controller into the ViewModel without splitting responsibilities, you get a Massive ViewModel.

**Better answer:** The root cause is missing separation of responsibilities, not the pattern itself. In MVC you can still extract services, separate data sources, child view controllers, and move navigation out. MVVM mainly helps by making presentation logic testable without UIKit, but business logic still needs its own service/use case layer.

### "Can you unit test a UIViewController? How do you test viewDidLoad?"

**Common wrong answer:** "You can't test it," or "just call `vc.viewDidLoad()` directly in the test."

**Better answer:** You can, but let UIKit drive the lifecycle: call `vc.loadViewIfNeeded()` so the view loads and `viewDidLoad` runs exactly once. Calling `viewDidLoad()` directly can make it run twice when `view` is accessed later. Things like `viewDidAppear` and push/present animations need a window, so they are slow and flaky; keep them thin and test the logic elsewhere.

## Exercise

Take a `ProductListViewController` that (1) calls URLSession directly, (2) formats prices inline, and (3) pushes to a detail screen. Identify what belongs in Model, Controller, and a separate Service. Sketch the separation in comments — no full code needed. Then explain what you could unit test if the code were structured that way, and what remains untestable in UIKit MVC regardless.
