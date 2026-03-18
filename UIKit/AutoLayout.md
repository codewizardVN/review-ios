[English](./AutoLayout.md) | [Tiếng Việt](./AutoLayout.vi.md)

[← UIKit and App Lifecycle](./README.md)

# Auto Layout

## Key Idea

Auto Layout is a constraint system. A reliable layout comes from clear priorities, intrinsic content size awareness, and avoiding ambiguous or conflicting constraints.

## What To Review

- Constraint priorities
- `contentHuggingPriority` and `contentCompressionResistancePriority`
- `UIStackView` strengths and limits
- Debugging unsatisfiable constraints

## Practice Questions

- Why does a label get compressed unexpectedly?
- When should you use `UIStackView` and when not?

## Senior Take

Most layout bugs are not “Auto Layout is broken” problems. They are ownership and constraint-definition problems. A senior answer should connect symptoms to the specific conflicting rule.

## Exercise

Build a profile header with avatar, name, subtitle, and action button. Explain how you would set priorities so long names truncate correctly while the button remains tappable.
