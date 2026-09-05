[English](./WidgetsLiveActivities.md) | [Tiếng Việt](./WidgetsLiveActivities.vi.md)

[← SwiftUI](./README.md)

# Widgets and Live Activities

## Key Idea

A widget extension is a separate process with its own memory and execution budget — it renders a snapshot of state on a timeline the system controls, not a live view of your running app. Live Activities extend that model to real-time, frequently-updated state on the Lock Screen and Dynamic Island.

## What To Review

- `TimelineProvider` / `AppIntentTimelineProvider` — supplies a list of `TimelineEntry` values with dates; the system renders whichever entry's date has passed, on its own schedule, not yours
- Widget families (`systemSmall/Medium/Large`, `accessoryCircular/Rectangular/Inline`) — layout must adapt per family, and Lock Screen accessory widgets render in a tinted, monochrome mode
- Data sharing — a widget extension can't access the host app's in-memory state; data must cross via App Group container (shared `UserDefaults`, file, or SQLite/Core Data store)
- `WidgetCenter.shared.reloadTimelines(ofKind:)` — how the host app requests a widget refresh instead of relying on the widget's own timeline (subject to a system-wide reload budget)
- ActivityKit / Live Activities — `Activity<Attributes>`, static `ContentState` vs frequently-updated content, started from the app, updated via push (`content-state` payload) or locally with a budget
- Dynamic Island layout regions — compact leading/trailing, minimal, expanded — each needs its own view, and expanded content still has to stay lightweight
- End-of-life handling — a Live Activity has a hard 8-hour default lifetime (extendable) and must be explicitly ended, or it becomes stale on the Lock Screen
- Deep linking — widgets and Live Activities open the app via `widgetURL(_:)` or `Link`, not by holding a reference to app state

## Example

```swift
struct DeliveryAttributes: ActivityAttributes {
    struct ContentState: Codable, Hashable {
        var etaMinutes: Int
        var status: String
    }
    var orderId: String
}

// Starting from the app
let activity = try Activity<DeliveryAttributes>.request(
    attributes: DeliveryAttributes(orderId: "123"),
    content: .init(state: .init(etaMinutes: 20, status: "Preparing"), staleDate: nil)
)
```

## Practice Questions

- Why can't a widget just read the app's `@Observable` view model directly?
- What happens to a Live Activity's Lock Screen UI if push updates stop arriving?
- Why does the system limit how often `reloadTimelines` actually triggers a redraw?

## Senior Take

Widget and Live Activity questions test whether you understand process boundaries. The common mistake is designing a widget like it's just another SwiftUI screen with live bindings — it isn't. A strong answer names the actual data path (App Group, push payload, timeline entry) end-to-end and accounts for staleness: what the user sees when the underlying data hasn't refreshed in a while, and how the design fails gracefully rather than showing silently wrong information.

## Exercise

Design a Live Activity for a food-delivery order: it should show ETA and status on the Lock Screen and update as the order progresses, without requiring the app to stay open. Specify the `ContentState` shape, whether updates come from local scheduling or server push, how you handle the order being cancelled after the activity started, and what the widget shows if the backend stops sending updates for 30 minutes.
