[English](./Localization.md) | [Tiếng Việt](./Localization.vi.md)

[← Accessibility and Localization](./README.md)

# Localization and Internationalization

## Key Idea

Localization isn't translating strings after the UI is built — layout, formatting, and pluralization have to be designed for variable-length, variable-direction, variable-grammar text from the start, or every translated locale becomes a bug report.

## What To Review

- String Catalogs (`.xcstrings`, since Xcode 15) — replace `Localizable.strings` + `.stringsdict` with a single file; on every build Xcode auto-extracts the string literals used as localization keys (in SwiftUI `Text`, `String(localized:)`, `LocalizedStringResource`, `NSLocalizedString`…) into the catalog, and tracks each key's translation state per locale
- Pluralization — write a string with a numeric interpolation, e.g. `String(localized: "\(count) items")`, then choose "Vary by Plural" for that key in the String Catalog (formerly a `.stringsdict`); at runtime the right form is picked from the number and the locale. "1 item" vs "5 items" isn't just English `%d` — under CLDR rules some languages have up to six plural categories (`zero`, `one`, `two`, `few`, `many`, `other`)
- `FormatStyle` — locale-aware formatting for dates, numbers, currency, measurements (`.formatted(.currency(code:))`, `.formatted(date:time:)`) instead of hand-built strings, which silently break for RTL or different decimal/grouping separators
- Right-to-left layout — `layoutDirection` environment value, leading/trailing (not left/right) constraints and stack alignment, mirrored vs non-mirrored SF Symbols
- Text expansion — German/Finnish strings typically run about 30–40% longer than English, and short strings (one- or two-word labels) can be twice as long or more; fixed-width buttons and truncated labels are the most common localization bug
- Locale-independent identifiers — never use a displayed, localized string as a lookup key or persisted value (e.g., don't switch on a localized day name)
- Testing — pseudo-localization: in the Xcode scheme editor (Run → Options → App Language) pick "Double-Length Pseudolanguage" (every string doubled in length) or "Right-to-Left Pseudolanguage" (layout flipped as in Arabic) to catch layout bugs, truncated text and unlocalized strings without waiting for real translations

## Example

```swift
// A key with a numeric interpolation → "%lld items in cart" in the String Catalog, set to "Vary by Plural".
// At runtime the right plural form is picked from `count` and the locale.
Text("\(count) items in cart", comment: "Number of items in the cart")

// The amount and its currency code travel together in the data (server/StoreKit).
struct Price {
    let amount: Decimal
    let currencyCode: String   // e.g. "USD" — belongs to the data, not the device
}

let price = Price(amount: 12.5, currencyCode: "USD")
// The user's locale only decides HOW it's shown ("$12.50", "12,50 $"…), not which currency it is.
Text(price.amount, format: .currency(code: price.currencyCode))
```

## Practice Questions

- Why is `String(format: "%d items", count)` wrong for shipping to Arabic or Russian locales?
- What breaks in a UIKit layout built with `.left`/`.right` constraints when the app runs in Arabic?
- Why shouldn't a feature flag or analytics event ever be keyed off a localized string?

## Senior Take

Localization questions test whether "ship in English first, translate later" was ever a safe assumption on this team. It never fully is — text expansion, RTL mirroring, and plural rules are structural layout and data-model decisions, not last-mile string swaps. A senior answer names a concrete case where retrofitting localization required real engineering work (rewriting fixed-width UI, replacing hand-built date strings) rather than treating it as a translation-team problem.

## Practice Question Answers

### Why is `String(format: "%d items", count)` wrong for shipping to Arabic or Russian locales?

Because it assumes English grammar, where "items" has one form for every number, while Russian has three plural forms and Arabic has six.

English only distinguishes "one" and "other". Under the CLDR rules Apple uses, for integers Russian has `one` (1, 21, 31… except 11), `few` (2–4, 22–24… except 12–14), `many` (0, 5–20, 25–30…), plus `other` for decimals; and Arabic has `zero`, `one`, `two`, `few`, `many`, `other`. The `"%d items"` string has three stacked bugs:

- "items" is hard-coded English and never goes through translation.
- A single format can't pick the right word form for the number.
- `String(format:)` passes no locale (unlike `String(format:locale:)`), so numbers aren't formatted for the user's locale (e.g. Arabic-Indic digits, grouping separators).

The right way is to let the String Catalog choose the plural form:

```swift
let label = String(localized: "\(count) items in cart",
                   comment: "Number of items in the cart")
// In .xcstrings: key "%lld items in cart" → Vary by Plural
```

Translators fill in each category their language needs; at runtime the right form is picked from `count` and the locale.

Trade-off: plural variation only solves counting. Gender, grammatical case, or plurals in a sentence with two variables still need the translator to see context — write a clear `comment` for every key.

### What breaks in a UIKit layout built with `.left`/`.right` constraints when the app runs in Arabic?

`.left`/`.right` constraints are fixed physical directions, so they don't flip for a right-to-left layout, and the whole screen still reads like English even though the text is Arabic.

In RTL, users read right to left, so their eyes look for the title, avatar and back button on the right. UIKit flips `.leading`/`.trailing` automatically based on `effectiveUserInterfaceLayoutDirection`; `.left`/`.right` it does not. Common results:

- The avatar stays on the left while the text is right-aligned, so the layout looks backwards and messy.
- `NSTextAlignment.left` instead of `.natural` misaligns Arabic text.
- `UIEdgeInsets` with `left`/`right` instead of `NSDirectionalEdgeInsets`.
- Chevrons and "next" arrows don't flip and point the wrong way; custom images need `imageFlippedForRightToLeftLayoutDirection()`.
- Slide animations using a positive `translationX` assume "moving right means forward".

The fix: switch everything to leading/trailing, use directional insets, and test with the RTL pseudolanguage in the scheme.

Trade-off: not everything should flip. Phone numbers, clocks, logos, icons of real-world objects, and views intentionally set to `semanticContentAttribute = .forceLeftToRight` (e.g. a number pad) must keep their direction.

### Why shouldn't a feature flag or analytics event ever be keyed off a localized string?

Because a localized string changes with the user's language and with every translation fix, so the same thing ends up with many different keys and the data falls apart.

A key must be stable and identical for every user. A displayed string isn't:

- A Vietnamese user sends event `"Thanh toán"`, an English user sends `"Checkout"` — the dashboard counts two events and per-locale funnels are completely wrong.
- A translator fixes a typo, the key changes, and historical data silently breaks.
- A flag looked up by display name won't match in another locale, so the feature silently turns off (or on) incorrectly.
- String comparison is locale-dependent, e.g. the Turkish "i", which causes bugs when lowercasing.

The right way is a stable identifier that is never shown to users, and localizing only in the presentation layer:

```swift
enum CheckoutStep: String { case cart, payment, review }
Analytics.log(event: .stepViewed(step: .payment))   // fixed key
Text("checkout.step.payment")                        // display only
```

Trade-off: if you need to know which language the user uses, send `Locale.current.identifier` as a separate property, not mixed into the event name.

## Interview Traps

### "Are `Text(product.name)` and `Text("welcome_title")` both localized?"

**Common wrong answer:** Yes, `Text` always looks up the String Catalog, so anything you pass gets translated.

**Better answer:** Only a string literal is treated as a `LocalizedStringKey` and looked up. When you pass a `String` variable, SwiftUI uses the `Text<S: StringProtocol>` initializer and shows it verbatim, untranslated. That's correct for server data (a product name), but a bug if you pass a key through a variable. To pass keys across layers, use `LocalizedStringResource` or `LocalizedStringKey`, not `String`.

### "Is formatting the price with `Locale.current` enough to handle currency?"

**Common wrong answer:** Yes, `.currency(code: Locale.current.currency?.identifier ?? "USD")` will show the right money for every user.

**Better answer:** `FormatStyle` only changes presentation (symbol, decimal separator, symbol position), not the exchange rate. Taking 12.5 and formatting it with the device locale's currency turns 12.5 USD into "12,50 €" for a user in Germany, or just 12–13 ₫ for a user in Vietnam — a wrong number. Currency is business data that must travel with the amount from the server or StoreKit (`product.displayPrice` is already formatted for the user's storefront); the locale only decides the formatting. That's why the file's example uses `.currency(code: price.currencyCode)`, with the currency code taken from the price data itself.

### "String Catalogs require an iOS 17 deployment target, right?"

**Common wrong answer:** Right, `.xcstrings` is new so it only works on iOS 17+; apps still supporting iOS 15 must keep `Localizable.strings`.

**Better answer:** String Catalogs are an Xcode feature (since Xcode 15), not a runtime feature. At build time Xcode compiles `.xcstrings` into `.strings` / `.stringsdict` in the bundle, so the app still runs on older iOS versions. The real benefits are automatic key extraction from code, plural and device variations in one file, and per-locale translation state tracking (new, stale, needs review).

## Exercise

A checkout screen shows: "You saved $12.50 (20%) — 3 items in cart, free shipping over $50." Rewrite this using String Catalog keys and `FormatStyle` so it's correct for a right-to-left, non-English locale with different currency, decimal separator, and plural rules — and explain what UI layout assumptions (fixed widths, `.left`/`.right` constraints, icon mirroring) would need to change to support it.
