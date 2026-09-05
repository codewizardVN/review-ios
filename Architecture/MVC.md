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

## Exercise

Take a `ProductListViewController` that (1) calls URLSession directly, (2) formats prices inline, and (3) pushes to a detail screen. Identify what belongs in Model, Controller, and a separate Service. Sketch the separation in comments — no full code needed. Then explain what you could unit test if the code were structured that way, and what remains untestable in UIKit MVC regardless.
