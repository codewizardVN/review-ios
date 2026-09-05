[English](./Accessibility.md) | [Tiếng Việt](./Accessibility.vi.md)

[← Accessibility and Localization](./README.md)

# Accessibility

## Key Idea

Accessibility is not a VoiceOver-only checkbox. It's whether the interface still works when any one input or output channel is degraded — sight, hearing, motor control, or reading fluency — and it's tested by using the app that way, not by reading the code.

## What To Review

- VoiceOver basics — `accessibilityLabel`, `accessibilityValue`, `accessibilityHint`, `accessibilityTraits`; label describes *what*, value describes *state*, hint describes *what happens if activated*
- Grouping and traversal — `accessibilityElement(children:)`, custom traversal order (`accessibilitySortPriority` / `accessibilityElements`) so VoiceOver reads content in a sensible order, not DOM/z-order
- Dynamic Type — `.font(.body)` with system text styles scales automatically; a hardcoded point size does not; layouts must reflow, not just get cut off, at accessibility sizes (up to `.accessibility5`)
- Custom actions — `accessibilityActions` / `UIAccessibilityCustomAction` to expose swipe-only gestures (e.g., "delete", "archive") to VoiceOver users who can't swipe on a cell
- Reduce Motion / Reduce Transparency — `UIAccessibility.isReduceMotionEnabled`, checked before non-essential animations or parallax effects
- Color contrast and "don't rely on color alone" — pairing a color-coded status with an icon or text label for color-blind users
- Focus management — moving VoiceOver focus (`UIAccessibility.post(notification: .screenChanged, argument:)`) after a sheet presents or a list updates, so focus doesn't get silently stranded
- Accessibility Inspector and the Audit tool in Xcode — automated checks (contrast, missing labels, tappable area size) as a first pass, not a replacement for manual VoiceOver testing

## Example

```swift
Button {
    toggleFavorite()
} label: {
    Image(systemName: isFavorite ? "heart.fill" : "heart")
}
.accessibilityLabel("Favorite")
.accessibilityValue(isFavorite ? "On" : "Off")
.accessibilityAddTraits(.isButton)
```

## Practice Questions

- Why is `accessibilityLabel("Heart icon")` on a favorite button a bad label?
- What breaks in a fixed-height cell design when a user sets the largest Dynamic Type size?
- Why does a custom-drawn chart (Canvas/Core Graphics) need explicit accessibility work that a native `List` gets for free?

## Senior Take

Accessibility questions separate people who've actually turned on VoiceOver from people who've only read about `accessibilityLabel`. The strong signal is describing a concrete failure you found by testing with VoiceOver or at max Dynamic Type — a control that was unreachable, a label that read the wrong thing, a layout that clipped — and how the fix changed the underlying view structure, not just added a label as an afterthought.

## Exercise

Take a custom card component that shows a product image, name, price, a strikethrough original price, and a "20% off" badge as a colored corner ribbon. Specify: the VoiceOver reading order and combined label/value, how the discount is conveyed without relying on the ribbon's color alone, what changes at the largest Dynamic Type size, and one custom action you'd add for VoiceOver users equivalent to a swipe gesture sighted users have.
