[English](./Navigation.md) | [Tiếng Việt](./Navigation.vi.md)

[← SwiftUI](./README.md)

# Navigation

## What To Review

- `NavigationStack` — replaces `NavigationView` in iOS 16+
- `NavigationPath` — type-erased stack for programmatic navigation
- `.navigationDestination(for:)` — data-driven destination mapping
- Sheet, fullScreenCover, popover — modal presentations
- Deep linking via `NavigationPath` or `openURL`

## Example

```swift
struct AppView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            FeedView()
                .navigationDestination(for: Item.self) { item in
                    ItemDetailView(item: item)
                }
        }
    }
}
```

## Practice Questions

- How would you pre-populate a NavigationStack's NavigationPath on app launch so a deep link navigates directly to the Reviews screen for a specific item, skipping the List and Detail screens?

## Senior Take

Prefer data-driven navigation (`.navigationDestination`) over inline `NavigationLink(destination:)`. It decouples the trigger from the destination and enables programmatic deep linking without knowing the full view hierarchy.

## Exercise

Build a 3-screen app using `NavigationStack` with `NavigationPath`: List → Detail → Reviews. Add a "Go to Root" button on the Reviews screen that clears the path with `path.removeLast(path.count)`. Then support programmatic deep link: on app launch, pre-populate `NavigationPath` to navigate directly to the Reviews screen for a specific item.
