[English](./DeepLinks.md) | [Tiếng Việt](./DeepLinks.vi.md)

[← UIKit and App Lifecycle](./README.md)

# Deep Links, Universal Links, and Notification Flows

## Key Idea

External entry points should map into app routes predictably, even when the app is cold-launched, backgrounded, or already inside another flow.

## What To Review

- URL parsing and route modeling: turn a URL (a custom scheme like `myapp://` or a universal link `https://`) into a strongly typed `Route` enum, so the rest of the app never works with raw URL strings.
- Authentication gating: before navigating, check whether the route requires login or some permission.
- Deferred navigation until app state is ready: on cold launch the UI, session, and data may not be ready yet, so the route must be held and only executed once the app signals it is ready.
- Push notifications as navigation intents: a notification tap is also an external entry point, so the `userInfo` payload should go through the same parser and router as URLs.

## Practice Questions

- What happens if a deep link arrives before login finishes?
- Where should route parsing live?

## Senior Take

Deep link handling is an app-level coordination problem. Strong answers talk about route modeling, readiness checks, fallback behavior, and analytics, not just opening a screen directly.

## Practice Question Answers

### What happens if a deep link arrives before login finishes?

The app should hold the deep link as a "pending route", let the user finish logging in, and only then navigate to it. Two common wrong approaches are dropping the link (the user taps it and nothing happens) and opening the protected screen directly (leaking data or crashing because there is no session yet).

A sensible flow:

1. The parser turns `myapp://orders/123` into `Route.orderDetail(id: "123")`.
2. The app-level router checks whether this route requires login and whether the session is ready.
3. If not, it stores `pendingRoute` and shows the login screen.
4. When login succeeds, the router takes `pendingRoute`, checks again (is this user allowed to see order 123?), navigates, and clears `pendingRoute`.

A few edge cases to handle:

- The user cancels login: drop the route and go to the default screen.
- The user logs in with a different account: the order may not belong to them, so you need a fallback screen like "Order not found".
- The route waits too long, for example the user leaves the app on the login screen all day: give it an expiry.

"Before login finishes" also covers cold launch, while the app is still restoring the session from the Keychain. The router must wait for an "app is ready" signal, not just check whether the user is logged in. Trade-off: keep only one pending route. If a new link arrives it replaces the old one; queuing several links leads to confusing navigation.

### Where should route parsing live?

Parsing should live in a separate, pure-logic component that does one thing: turn external input (URL, universal link, push payload, shortcut item) into a `Route` enum. It should not live in the SceneDelegate or a view controller.

```swift
enum Route: Equatable {
    case orderDetail(id: String)
    case settings
}

struct DeepLinkParser {
    func route(from url: URL) -> Route? {
        let parts: [String]
        switch url.scheme {
        case "myapp":
            // myapp://orders/123: host is "orders", path is "/123"
            parts = [url.host ?? ""] + url.pathComponents.dropFirst()
        case "https" where url.host == "example.com":
            // https://example.com/orders/123: path is "/orders/123"
            parts = Array(url.pathComponents.dropFirst())
        default:
            return nil // unknown scheme or domain: ignore
        }

        switch parts {
        case ["settings"]:
            return .settings
        case let p where p.count == 2 && p[0] == "orders" && !p[1].isEmpty:
            return .orderDetail(id: p[1]) // the id must still be re-checked at the data layer
        default:
            return nil
        }
    }
}
```

This example handles both `myapp://orders/123` (host is `orders`) and `https://example.com/orders/123` (path is `/orders/123`), so both kinds of link produce the same `Route`. It also checks the scheme and domain, and returns `nil` for any URL it does not recognize so the router can show a default screen instead of crashing. Benefits:

- It can be tested with simple unit tests, without running any UI.
- Custom schemes, universal links, and push share one place, so their logic cannot drift apart.
- The SceneDelegate only forwards data, and the router or coordinator only handles navigation. Each has one clear responsibility.

The parser is also where validation happens, because a URL is external, untrusted input. Trade-off: for a small app with a few routes, a single `switch` function is enough; you do not need a complex routing framework.

## Interview Traps

### "On a cold launch from a URL, does the code in scene(_:openURLContexts:) run?"

**Common wrong answer:** Yes, every URL goes through `scene(_:openURLContexts:)`.

**Better answer:** That method only runs when the scene already exists, meaning the app is running or in background. On cold launch the URL is in `connectionOptions.urlContexts` of `scene(_:willConnectTo:options:)`, and a universal link is in `connectionOptions.userActivities`. While the app is running, universal links arrive through `scene(_:continue:)`. If you only handle one place, the link "does nothing" in the most important case: the first launch.

### "Universal links are configured, so why does tapping one still open Safari?"

**Common wrong answer:** The AASA file is wrong; fix it on the server and it works immediately.

**Better answer:** There are several legitimate reasons. A link typed directly into Safari's address bar does not open the app. Tapping a link on the same domain inside Safari often does not open the app either. If the user once chose "Open in Safari", iOS remembers that choice. Also, since iOS 14 the device does not fetch the `apple-app-site-association` file directly from your server but through Apple's CDN, mainly when the app is installed or updated, not on every tap. The CDN also caches the file, so a server-side change does not take effect immediately. For debugging you can add `?mode=developer` to the associated domain (for example `applinks:example.com?mode=developer`) so the device fetches the file straight from your server; this requires turning on Associated Domains Development in the Developer section of Settings and only applies to development builds.

### "A deep link carries an action, like myapp://pay?amount=100. Can you just execute it?"

**Common wrong answer:** Yes, the URL is defined by our own app, so trust it and perform the action.

**Better answer:** Custom URL schemes have no ownership mechanism; any app or website can call `myapp://` with arbitrary parameters. A deep link should only take the user to a screen, never perform a side effect on its own such as paying, deleting data, or changing settings. Validate every parameter and ask the user to confirm inside the app. Universal links are safer about origin because they are tied to a domain, but their parameters are still untrusted input.

## Exercise

Design routing for `myapp://orders/123` and a universal link to the same order. Explain how the app behaves when launched cold, when already on another tab, and when the user is not authenticated.
