[English](./AutoLayout.md) | [Tiếng Việt](./AutoLayout.vi.md)

[← UIKit and App Lifecycle](./README.md)

# Auto Layout

## Key Idea

Auto Layout is a constraint system. A reliable layout comes from clear priorities, intrinsic content size awareness, and avoiding ambiguous or conflicting constraints.

## What To Review

- Constraint priorities: every constraint has a priority from 1 to 1000. 1000 (`.required`) is mandatory; Auto Layout must satisfy it, and if it cannot, it reports an unsatisfiable-constraints error and breaks one constraint itself. Below 1000 is optional: Auto Layout tries to satisfy it, and on a conflict the lower-priority constraint gives way.
- `contentHuggingPriority` and `contentCompressionResistancePriority`: two implicit priorities that every view with content (label, button, image view) uses to protect its `intrinsicContentSize`, one resisting being stretched, one resisting being squeezed (see the interview traps below).
- `UIStackView` strengths and limits
- Debugging unsatisfiable constraints: read the "Unable to simultaneously satisfy constraints" log in the console (it lists the conflicting constraints and the one the system breaks), set an `identifier` on constraints so the log is readable, add a symbolic breakpoint on `UIViewAlertForUnsatisfiableConstraints` to stop exactly when it happens, and use Xcode's View Debugger to inspect each view's constraints. Ambiguous layouts produce no error log; you can check them with `view.hasAmbiguousLayout` while debugging.

## Practice Questions

- Why does a label get compressed unexpectedly?
- When should you use `UIStackView` and when not?

## Senior Take

Most layout bugs are not “Auto Layout is broken” problems. They are ownership and constraint-definition problems. A senior answer should connect symptoms to the specific conflicting rule.

## Practice Question Answers

### Why does a label get compressed unexpectedly?

A label gets compressed because another constraint in the system has a higher priority than the label's compression resistance, so Auto Layout chooses to sacrifice the label. By default a label's `contentCompressionResistancePriority` is 750 (`.defaultHigh`), while constraints you create default to 1000 (`.required`). When space runs out, the 1000 constraint always wins and the label gets cut.

Common causes:

- Two labels side by side with the same compression resistance. The layout is ambiguous and Auto Layout picks one to compress, sometimes the very name label you wanted to keep.
- A neighbouring view (button, icon) has a fixed width at priority 1000, or a stack view uses `.fillEqually` to split the space evenly.
- A multi-line label in a cell still has `numberOfLines` set to 1, or the cell is not self-sizing so its height is locked.

The fix is to tell Auto Layout the order of priority explicitly. For the profile header in the exercise:

```swift
actionButton.setContentCompressionResistancePriority(.required, for: .horizontal)
actionButton.setContentHuggingPriority(.required, for: .horizontal)
nameLabel.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
nameLabel.lineBreakMode = .byTruncatingTail
```

The button keeps its size and tap area, and a long name truncates with "...". Trade-off: do not fix this by giving the label a fixed width, because that breaks with Dynamic Type and other languages.

### When should you use `UIStackView` and when not?

Use `UIStackView` when views line up in a single row or column and you want the system to handle spacing, alignment, and showing/hiding. Its biggest strength: when you set `isHidden = true` on an arranged subview, the stack view removes it from the layout and closes the gap, with no constraint changes. It also works well with Dynamic Type, for example switching `axis` from horizontal to vertical when text gets too large.

Do not use it when:

- The layout is not linear: overlapping views, aligning to the baseline of a view in another row, or relationships between two views that are not in the same stack. Nesting stacks several levels deep to "force" such a layout is harder to read than writing constraints directly.
- Cells in a very long list use many nested stacks. Each stack generates extra internal constraints, and together they add layout time during fast scrolling.
- You need fine control over the priority of each individual spacing.

A version note: before iOS 14 a stack view did not render anything, so `backgroundColor` had no effect. From iOS 14 it works. General trade-off: stack views keep code short and easy to change, but when a layout bug appears you must understand the constraints they create for you.

## Interview Traps

### "What is the difference between content hugging and compression resistance?"

**Common wrong answer:** They are basically the same; the higher the priority, the more the view "keeps" its size.

**Better answer:** The two priorities act in opposite directions. Hugging resists being stretched **larger** than the intrinsic size, so a view with high hugging will not expand to fill empty space. Compression resistance resists being squeezed **smaller** than the intrinsic size, so a view with high resistance will not be truncated. In a row with a label and a button, you usually want the label to have low hugging (it can stretch) and lower resistance than the button (it gets cut first).

### "You create a view in code and add constraints, but the layout is still broken. Why?"

**Common wrong answer:** The constraints have rounding errors; call `layoutIfNeeded()` or add another constraint to be safe.

**Better answer:** The classic cause is forgetting `translatesAutoresizingMaskIntoConstraints = false`. For views created in code it defaults to `true`, so UIKit generates `NSAutoresizingMaskLayoutConstraint`s from the frame, and they conflict with yours. The unsatisfiable-constraints log will contain `NSAutoresizingMaskLayoutConstraint` lines, which is the tell. `NSLayoutConstraint.activate` does not turn this flag off for you, while views from Interface Builder already have it off.

### "Can you change a constraint's priority at runtime to toggle a layout?"

**Common wrong answer:** Yes, just change `priority` from 1000 to 250 and back.

**Better answer:** Changing priority between optional values (below 1000) is fine. But changing from `.required` to non-required, or the reverse, on an active constraint throws an exception. Use 999 instead of 1000 if you need to change it, or keep two constraints and toggle them with `isActive` (deactivate the old one before activating the new one to avoid a temporary conflict).

## Exercise

Build a profile header with avatar, name, subtitle, and action button. Explain how you would set priorities so long names truncate correctly while the button remains tappable.
