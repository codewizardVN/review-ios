[English](./Navigation.md) | [Tiếng Việt](./Navigation.vi.md)

[← SwiftUI](./README.md)

# Navigation

## What To Review

- `NavigationStack` — replaces the (deprecated) `NavigationView` from iOS 16+; for multi-column layouts (iPad, Mac) use `NavigationSplitView`.
- `NavigationPath` — a type-erased stack (it can hold several different `Hashable` types) for programmatic navigation: push is `append`, pop is `removeLast`. If the stack only has one route type, a typed array like `[Route]` works as the path too.
- `.navigationDestination(for:)` — maps "data type → screen": when the path contains a value of that type, SwiftUI builds the matching screen. The trigger (`NavigationLink(value:)` or a path change) is decoupled from the destination.
- Sheet, fullScreenCover, popover — modal presentations, driven by a `Bool` (`isPresented:`) or an optional `Identifiable` (`item:`), and not part of the navigation path. On iPhone a popover shows as a sheet by default (from iOS 16.4 you can change that with `.presentationCompactAdaptation(.popover)`).
- Deep linking — receive the URL with `.onOpenURL` (or `onContinueUserActivity` for universal links delivered as `NSUserActivity`), parse it into routes and assign them to the path. (The `openURL` environment action is for *opening* a URL, not receiving one.)

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

## Practice Question Answers

### How would you pre-populate a NavigationStack's NavigationPath on app launch so a deep link navigates directly to the Reviews screen for a specific item, skipping the List and Detail screens?

Parse the deep link into an array of routes and assign the whole array to the `NavigationStack`'s path — e.g. `[.detail(id), .reviews(id)]` — before or as soon as the stack appears; SwiftUI builds the entire stack at once with Reviews on top.

Mechanism: `NavigationStack(path:)` treats the path as the source of truth. Each element in the path is mapped to a screen through a `.navigationDestination(for:)` registered at the root. Because destinations are chosen by data rather than by a `NavigationLink` sitting inside List or Detail, you don't need to "tap through" each screen. List is still the root and Detail is still in the stack, so Back from Reviews returns to Detail as usual.

```swift
enum Route: Hashable { case detail(Item.ID), reviews(Item.ID) }

@State private var path: [Route] = []

NavigationStack(path: $path) {
    ListView()
        .navigationDestination(for: Route.self) { route in
            switch route {
            case .detail(let id): ItemDetailView(itemID: id)
            case .reviews(let id): ReviewsView(itemID: id)
            }
        }
}
.onOpenURL { url in
    if let id = DeepLink.itemID(from: url) { path = [.detail(id), .reviews(id)] } // your own helper
}
```

`onOpenURL` is also called when the app cold-launches from a URL. Pass IDs rather than whole models so each screen loads its own data. Trade-off: a typed `[Route]` array is easier to inspect and test than `NavigationPath`; use `NavigationPath` only when the stack really holds several different types. The "Go to Root" button then just needs `path.removeAll()`.

## Interview Traps

### "You can put .navigationDestination anywhere, as long as it is inside the NavigationStack?"

**Common wrong answer:** Attaching `.navigationDestination(for:)` to each row inside a `List` or `LazyVStack`, close to the `NavigationLink(value:)`.

**Better answer:** Destinations must be registered on a view that always exists in the stack, usually the root, not inside a lazy container. A row in a lazy container may not have been created yet or may already be destroyed, so SwiftUI can't find the destination and ignores the navigation, with a warning in the console. For deep links this is the most common bug: the path is correct but no screen appears because no destination is registered for that type.

### "NavigationLink(destination:) only creates the destination when the user taps it?"

**Common wrong answer:** Thinking the destination view is only initialized at navigation time, so doing heavy work in the destination's `init` is harmless.

**Better answer:** With `NavigationLink(destination:)`, the destination struct is initialized as soon as the `body` containing the link is evaluated — every row that gets built (and rebuilt on each re-render) means another Detail init, even though its `body` hasn't run. `List` is lazy so only rows actually being built pay, but in a plain `VStack` 100 rows means 100 inits. If `init` creates a view model or calls the network, that cost repeats. `NavigationLink(value:)` + `.navigationDestination` only builds the destination when the path actually contains that value, which is one more reason to prefer data-driven navigation.

### "To restore navigation state after the app is killed, just save the NavigationPath?"

**Common wrong answer:** Assuming `NavigationPath` can always be encoded because it is an Apple-provided type.

**Better answer:** `NavigationPath` can only be encoded when every element in it is `Codable`; the `path.codable` property returns `nil` if any element is not. The safe approach is an `enum Route: Hashable, Codable` holding only IDs, saving the path (for `NavigationPath`, encode `path.codable` — a `NavigationPath.CodableRepresentation`; for `[Route]`, encode the array directly) into `@SceneStorage` as `Data`, and on restore handling the case where the item no longer exists instead of opening an empty screen. Note: the system discards scene-restoration data when the user swipes the app away in the app switcher, so `@SceneStorage` only restores after the system kills the app in the background; if you need to survive that case too, persist to disk yourself.

## Exercise

Build a 3-screen app using `NavigationStack` with `NavigationPath`: List → Detail → Reviews. Add a "Go to Root" button on the Reviews screen that clears the path with `path.removeLast(path.count)`. Then support programmatic deep link: on app launch, pre-populate `NavigationPath` to navigate directly to the Reviews screen for a specific item.
