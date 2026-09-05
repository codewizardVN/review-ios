[English](./Localization.md) | [Tiếng Việt](./Localization.vi.md)

[← Accessibility and Localization](./README.md)

# Localization and Internationalization

## Key Idea

Localization isn't translating strings after the UI is built — layout, formatting, and pluralization have to be designed for variable-length, variable-direction, variable-grammar text from the start, or every translated locale becomes a bug report.

## What To Review

- String Catalogs (`.xcstrings`) — replaced `Localizable.strings` + `.stringsdict`; Xcode auto-extracts string literals wrapped in `String(localized:)` or SwiftUI `Text`, tracks translation state per locale
- Pluralization — `String(localized:, options: .init(...))` / stringsdict-style plural rules; "1 item" vs "5 items" isn't just English `%d` — some locales have more than two plural categories
- `FormatStyle` — locale-aware formatting for dates, numbers, currency, measurements (`.formatted(.currency(code:))`, `.formatted(date:time:)`) instead of hand-built strings, which silently break for RTL or different decimal/grouping separators
- Right-to-left layout — `layoutDirection` environment value, leading/trailing (not left/right) constraints and stack alignment, mirrored vs non-mirrored SF Symbols
- Text expansion — German/Finnish strings can run 30-50% longer than English; fixed-width buttons and truncated labels are the most common localization bug
- Locale-independent identifiers — never use a displayed, localized string as a lookup key or persisted value (e.g., don't switch on a localized day name)
- Testing — pseudo-localization and the "Double-Length Pseudolanguage" / RTL pseudolanguage schemes in the Xcode scheme editor to catch layout and text-key bugs without waiting for real translations

## Example

```swift
Text("cart_item_count", comment: "Number of items in the cart")
    // resolves via String Catalog, picks the right plural form per locale

let price = 12.5
Text(price, format: .currency(code: currentLocale.currency?.identifier ?? "USD"))
```

## Practice Questions

- Why is `String(format: "%d items", count)` wrong for shipping to Arabic or Russian locales?
- What breaks in a UIKit layout built with `.left`/`.right` constraints when the app runs in Arabic?
- Why shouldn't a feature flag or analytics event ever be keyed off a localized string?

## Senior Take

Localization questions test whether "ship in English first, translate later" was ever a safe assumption on this team. It never fully is — text expansion, RTL mirroring, and plural rules are structural layout and data-model decisions, not last-mile string swaps. A senior answer names a concrete case where retrofitting localization required real engineering work (rewriting fixed-width UI, replacing hand-built date strings) rather than treating it as a translation-team problem.

## Exercise

A checkout screen shows: "You saved $12.50 (20%) — 3 items in cart, free shipping over $50." Rewrite this using `String` catalog keys and `FormatStyle` so it's correct for a right-to-left, non-English locale with different currency, decimal separator, and plural rules — and explain what UI layout assumptions (fixed widths, `.left`/`.right` constraints, icon mirroring) would need to change to support it.
