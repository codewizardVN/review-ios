[English](./Accessibility.md) | [Tiếng Việt](./Accessibility.vi.md)

[← Accessibility and Localization](./README.md)

# Accessibility

## Key Idea

Accessibility is not a VoiceOver-only checkbox. It's whether the interface still works when any one input or output channel is degraded — sight, hearing, motor control, or reading fluency — and it's tested by using the app that way, not by reading the code.

## What To Review

- VoiceOver basics — `accessibilityLabel`, `accessibilityValue`, `accessibilityHint`, `accessibilityTraits`; label describes *what*, value describes *state*, hint describes *what happens if activated*
- Grouping and traversal — `accessibilityElement(children:)`, custom traversal order (`accessibilitySortPriority` in SwiftUI / the `accessibilityElements` array in UIKit) so VoiceOver reads content in an order that makes sense. By default VoiceOver follows on-screen position (top to bottom, in the language's reading direction) and the view hierarchy, so multi-column layouts or overlapping views are easily read in a jumbled order. `accessibilityElement(children: .combine)` merges several child views into one element so the user swipes once for the whole cell
- Dynamic Type — `.font(.body)` with system text styles scales automatically; a hardcoded point size does not; layouts must reflow, not just get cut off, at accessibility sizes (up to `.accessibility5`)
- Custom actions — `accessibilityActions` / `UIAccessibilityCustomAction` to expose swipe-only gestures (e.g., "delete", "archive") to VoiceOver users who can't swipe on a cell
- Reduce Motion / Reduce Transparency — UIKit reads `UIAccessibility.isReduceMotionEnabled` / `isReduceTransparencyEnabled`, SwiftUI reads `@Environment(\.accessibilityReduceMotion)` / `@Environment(\.accessibilityReduceTransparency)`. Check before non-essential animations or parallax effects (replace them with a crossfade), and swap blurred/translucent backgrounds for solid ones when Reduce Transparency is on
- Color contrast and "don't rely on color alone" — pairing a color-coded status with an icon or text label for color-blind users
- Focus management — moving VoiceOver focus after a sheet presents or a list updates, so focus doesn't get silently stranded on the old element. In UIKit: `UIAccessibility.post(notification: .screenChanged, argument: view)` when the whole screen changes (VoiceOver plays a sound and jumps to `view`), `.layoutChanged` when only part of the layout changes. In SwiftUI (iOS 15+): `@AccessibilityFocusState` together with `.accessibilityFocused(_:)`
- Accessibility Inspector and the Audit tool in Xcode — automated checks (contrast, missing labels, tappable area size) as a first pass, not a replacement for manual VoiceOver testing

## Example

```swift
// A SwiftUI Button already has the button trait — no need (and no reason) to add .isButton.
Button {
    toggleFavorite()
} label: {
    Image(systemName: isFavorite ? "heart.fill" : "heart")
}
.accessibilityLabel("Favorite")                 // what: the function's name, stable across states
.accessibilityValue(isFavorite ? "On" : "Off")  // current state

// Only a custom view using onTapGesture needs .isButton added by hand,
// because the system can't know it's tappable. Better still: make it a Button.
Image(systemName: "xmark")
    .onTapGesture { dismiss() }
    .accessibilityLabel("Close")
    .accessibilityAddTraits(.isButton)
```

## Practice Questions

- Why is `accessibilityLabel("Heart icon")` on a favorite button a bad label?
- What breaks in a fixed-height cell design when a user sets the largest Dynamic Type size?
- Why does a custom-drawn chart (Canvas/Core Graphics) need explicit accessibility work that a native `List` gets for free?

## Senior Take

Accessibility questions separate people who've actually turned on VoiceOver from people who've only read about `accessibilityLabel`. The strong signal is describing a concrete failure you found by testing with VoiceOver or at max Dynamic Type — a control that was unreachable, a label that read the wrong thing, a layout that clipped — and how the fix changed the underlying view structure, not just added a label as an afterthought.

## Practice Question Answers

### Why is `accessibilityLabel("Heart icon")` on a favorite button a bad label?

Because it describes what the icon looks like, not what the button does, so a VoiceOver user hears "Heart icon, button" and still doesn't know what tapping it will do.

A label answers "what is this" in functional terms. A sighted user understands that a heart means "favorite" from visual context; a VoiceOver user doesn't have that context. "Heart icon" also has three smaller problems:

- The word "icon" is noise: VoiceOver already announces the "button" trait, and the user doesn't need to know it's an image.
- It says nothing about state. Whether it's favorited is the job of `accessibilityValue`, as the file's example does with `"On"` / `"Off"`.
- It describes the image, not the function, so even when it is translated (a literal in SwiftUI's `.accessibilityLabel("...")` is treated as a `LocalizedStringKey`), users in other languages still just hear "heart icon". And if it's assigned from a `String` variable, or as `accessibilityLabel = "Heart icon"` in UIKit without `String(localized:)`, it isn't translated at all.

A good label is short, functional, and stable across states: `"Favorite"`. If you put state into the label (e.g. `"Unfavorite"` when on), users get confused because the same button changes its name. For an on/off button, iOS 17 adds the `.isToggle` trait so VoiceOver announces it as a switch, or you can just use a `Toggle`.

Trade-off: sometimes the label needs to be more specific when a list has many identical buttons, e.g. "Favorite, Blue jacket" — but then it's usually better to combine the whole cell with `accessibilityElement(children: .combine)` rather than making the label longer.

### What breaks in a fixed-height cell design when a user sets the largest Dynamic Type size?

Text gets clipped, overlaps, or truncates with "…", so key information like the price or product name disappears for exactly the people who need the largest text.

At `.accessibility5`, body text can be roughly three times the default size. A 60pt-tall cell fits only part of the first line. Typical failures:

- Labels clip or truncate because of fixed height/width.
- An icon + text `HStack` gets squeezed until the text is a few characters per line.
- Icons don't scale with the text, so they look misaligned.

The fix is to let the cell size itself (self-sizing), let text wrap with `lineLimit(nil)`, and change layout at accessibility sizes: switch from horizontal to vertical.

```swift
@Environment(\.dynamicTypeSize) private var size
@ScaledMetric private var iconSize = 24.0

var body: some View {
    let layout = size.isAccessibilitySize
        ? AnyLayout(VStackLayout(alignment: .leading))
        : AnyLayout(HStackLayout())
    layout {
        icon.frame(width: iconSize)
        details
    }
}
```

Trade-off: not every UI can reflow (tab bars, toolbars). There, use the Large Content Viewer, or cap that specific element with `.dynamicTypeSize(...DynamicTypeSize.accessibility2)` — sparingly, never for a whole screen.

### Why does a custom-drawn chart (Canvas/Core Graphics) need explicit accessibility work that a native `List` gets for free?

Because Canvas or Core Graphics only produces pixels, not elements in the accessibility tree, so to VoiceOver the whole chart is an empty area or an unnamed image.

A `List` is built from real views: each row has text, a frame, and traits, and the system turns them into accessibility elements in a sensible reading order. In a custom-drawn chart the data lives in drawing code that VoiceOver can't read. You have to provide:

- An overall summary: label "Revenue, last 7 days", value "highest on Friday, 12 million".
- An element per data point so the user can swipe through them, via `.accessibilityChildren { }` in SwiftUI, or `UIAccessibilityElement` with `accessibilityFrameInContainerSpace` in UIKit.
- Optionally `accessibilityChartDescriptor` (`AXChartDescriptor`, iOS 15+) to get Audio Graphs — hearing the chart as pitch.

Trade-off: a chart with 365 points where every point is an element means 365 swipes. Aggregate by week/month, or expose only the summary plus Audio Graph. When possible use Swift Charts: it generates default elements and a chart descriptor for you, far less work than Canvas.

## Interview Traps

### "Does this button need `.accessibilityAddTraits(.isButton)`?"

**Common wrong answer:** Yes, always add the `.isButton` trait to every button so VoiceOver knows it's a button.

**Better answer:** SwiftUI `Button` and `UIButton` already carry the button trait, so adding it again is redundant (harmless, but it shows you don't know the system defaults). `.isButton` is only needed on custom views using `onTapGesture` (like the `Image(systemName: "xmark")` + `onTapGesture` in the file's example), and the better answer there is to turn the view into a `Button` so it also gets activation, keyboard focus and Voice Control for free. What's worth adding to the favorite button is state: `.accessibilityValue` or `.isToggle` (iOS 17+).

### "The Xcode Accessibility Audit passes. Is the app accessible?"

**Common wrong answer:** Yes — if Accessibility Inspector and `performAccessibilityAudit()` in XCUITest (iOS 17+) report nothing, it meets the bar.

**Better answer:** The audit only catches machine-measurable issues: missing labels, low contrast, small hit targets, clipped text. It can't tell whether a label like "Button 3" makes sense, whether the reading order is logical, whether focus gets stranded after a sheet opens, or whether a flow is doable with Switch Control. The audit is a CI screening step; you still have to turn on VoiceOver and max Dynamic Type and walk the core flows yourself.

### "What do you do with animations when Reduce Motion is on?"

**Common wrong answer:** Turn off all animations and let everything jump straight to the new state.

**Better answer:** Reduce Motion targets motion that causes discomfort: zooms, parallax, large slides, spins. Replace those with gentle effects like a crossfade rather than removing visual feedback entirely, because users still need to see that state changed. In SwiftUI read `@Environment(\.accessibilityReduceMotion)` and choose `.opacity` instead of `.move`/`.scale`.

## Exercise

Take a custom card component that shows a product image, name, price, a strikethrough original price, and a "20% off" badge as a colored corner ribbon. Specify: the VoiceOver reading order and combined label/value, how the discount is conveyed without relying on the ribbon's color alone, what changes at the largest Dynamic Type size, and one custom action you'd add for VoiceOver users equivalent to a swipe gesture sighted users have.
