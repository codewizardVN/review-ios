[English](./WidgetsLiveActivities.md) | [Tiếng Việt](./WidgetsLiveActivities.vi.md)

[← SwiftUI](./README.md)

# Widgets and Live Activities

## Key Idea

A widget extension is a separate process with its own memory and execution budget — it renders a snapshot of state on a timeline the system controls, not a live view of your running app. Live Activities extend that model to real-time, frequently-updated state on the Lock Screen and Dynamic Island.

## What To Review

- `TimelineProvider` / `AppIntentTimelineProvider` — supplies a list of `TimelineEntry` values with dates; the system renders whichever entry's date has passed, on its own schedule, not yours
- Widget families (`systemSmall/Medium/Large`, `accessoryCircular/Rectangular/Inline`) — layout must adapt per family. Widgets can be rendered in different modes (read via `@Environment(\.widgetRenderingMode)`): Lock Screen accessory widgets render in `vibrant` mode (color removed, tinted by the system), and from iOS 18 Home Screen widgets can also be in `accented` (tinted) mode when the user picks tinted icons/widgets, so don't rely on color to convey information
- Data sharing — a widget extension can't access the host app's in-memory state; data must cross via App Group container (shared `UserDefaults`, file, or SQLite/Core Data store)
- `WidgetCenter.shared.reloadTimelines(ofKind:)` — how the host app requests a widget refresh instead of relying on the widget's own timeline (subject to a system-wide reload budget)
- ActivityKit / Live Activities — `Activity<Attributes>`: static data (like `orderId`) lives in the `ActivityAttributes` struct itself and never changes for the activity's life, while `ContentState` is the dynamic part that is updated frequently (ETA, status). The dynamic data sent in each update (local or push) is limited to 4 KB, so include only what the UI needs. An activity is started from the app (or by push-to-start from iOS 17.2), updated locally with `activity.update(_:)` while the app is running, or via ActivityKit push (`content-state` payload); high-priority pushes (`apns-priority: 10`) are subject to a system budget, and apps that need frequent updates can declare `NSSupportsLiveActivitiesFrequentUpdates` in Info.plist
- Dynamic Island layout regions — compact leading/trailing, minimal, expanded — each needs its own view, and expanded content still has to stay lightweight
- End-of-life handling — a Live Activity can be active for at most 8 hours; after that the system ends it, and an ended activity can stay on the Lock Screen for up to 4 more hours. You should end it explicitly with `activity.end(_:dismissalPolicy:)` or an `end` push when the event is over, otherwise the user sees stale data on the Lock Screen
- Deep linking — widgets and Live Activities open the app via `widgetURL(_:)` (one tap target for the whole widget) or `Link` (multiple tap targets, not available in `systemSmall`), not by holding a reference to app state
- Interactive widgets (iOS 17+) — `Button(intent:)` and `Toggle(isOn:intent:)` with an `AppIntent` let the user act directly on a widget/Live Activity without opening the app; the intent runs, writes data, then the system reloads the timeline to re-render. The view is still a snapshot with no live state

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

## Practice Question Answers

### Why can't a widget just read the app's `@Observable` view model directly?

Because the widget extension runs in a separate process, and an `@Observable` view model exists only in the app process's memory — two processes don't share objects.

Think of the app and the widget as two different programs packaged together. When the system needs the widget, it launches the extension (sometimes while the app isn't running at all), calls the `TimelineProvider` for entries, renders the view into a snapshot, and may then shut the extension down. At no point can the extension "see" into the app's heap, so `@Observable` observation tracking doesn't cross this boundary. Even if both targets compile the same `ViewModel.swift` file, each process has its own instance.

The correct data path:

- The app writes the state to display into the App Group container (shared `UserDefaults` with a `suiteName`, a JSON file, or a shared SwiftData/Core Data store).
- The app calls `WidgetCenter.shared.reloadTimelines(ofKind:)` after writing.
- The `TimelineProvider` reads from the App Group and builds entries.

Trade-off: widget data is always a delayed snapshot, so write only the minimum the widget needs (not the whole view model) and store a last-updated timestamp so the widget can show "updated at…" instead of pretending to be real-time.

### What happens to a Live Activity's Lock Screen UI if push updates stop arriving?

The UI stays frozen on the last `ContentState` it received — the system doesn't refresh it or show an error on its own, so the user will see an ETA of "20 minutes" until the activity expires (at most 8 hours active, plus up to 4 more hours on the Lock Screen) unless you design for this case.

A Live Activity doesn't run code or fetch data by itself; it only re-renders when a new update arrives from the app or from a push. There are three mechanisms for dealing with staleness:

- `staleDate`: set it when starting or send it with each update (`stale-date` in the push payload). Once that time passes, `context.isStale` becomes `true` and the view can show "Updating…" or dim the ETA.
- Maximum duration: after 8 hours the system ends the activity; once ended it can stay on the Lock Screen for up to 4 more hours (unless you set a different dismissal policy or the user removes it).
- Explicit end: the backend should send an `end` event with the final state and a `dismissal-date` when the order completes or is cancelled.

For the exercise's 30 minutes without updates: set `staleDate` a few minutes after the expected ETA, and when stale replace the ETA with a neutral message like "Waiting for an update from the restaurant" instead of a number that may be wrong.

### Why does the system limit how often `reloadTimelines` actually triggers a redraw?

Because every reload costs battery and system resources, and widgets are glanceable rather than real-time screens, so WidgetKit treats `reloadTimelines` as a request, not a command.

Each reload means the system must wake the extension process, run the `TimelineProvider` (which may read disk or hit the network), then render and store snapshots for every family on screen. Multiply that by dozens of widgets on one device, and letting apps reload at will would drain the battery noticeably. So each widget has a daily reload budget (Apple's docs describe roughly 40–70 per day for a frequently viewed widget), and the system coalesces nearby requests and picks the timing itself. Some cases don't count against the budget, for example when the app is in the foreground or has an active audio/navigation session.

The right design avoids needing reloads: supply many future entries in one timeline, use `Text(date, style: .timer)` or `.relative` for clocks so the system updates them without a reload, and move to a Live Activity when the data really changes minute by minute.

## Interview Traps

### "To make a widget count down every second, use a Timer or reload every second?"

**Common wrong answer:** Putting `Timer.publish` / `onReceive` in the widget view, or building a timeline with entries one second apart.

**Better answer:** A widget view is rendered into a snapshot and archived; no code runs inside it continuously, so the `Timer` never fires. Per-second entries also waste budget, and the system doesn't guarantee they display on time. Use views the system animates for you: `Text(endDate, style: .timer)`, `Text(timerInterval: start...end)`, or `ProgressView(timerInterval:)`; they update every second with no reload.

### "A Live Activity's view can call an API itself to fetch a new ETA?"

**Common wrong answer:** Thinking a Live Activity is a mini-app, so its view can use `URLSession` or receive location updates to refresh itself.

**Better answer:** Live Activities run in a sandbox with no network access and no location updates. Content only changes when the app calls `activity.update(_:)` (the app must be running, even if in the background) or when the server sends an ActivityKit push (`apns-push-type: liveactivity`) containing a new `content-state`. Since the app is usually suspended, server push is the reliable update path for a delivery order.

### "A Live Activity can only be started while the app is in the foreground?"

**Common wrong answer:** Stating that `Activity.request` is the only way, so if the user orders on the web, no Live Activity can appear until they open the app.

**Better answer:** True for iOS 16.1–17.1, but since iOS 17.2 there is push-to-start: the app gets a token via `Activity<DeliveryAttributes>.pushToStartTokenUpdates`, sends it to the server, and the server can start the activity by push while the app isn't running. However it's started, the user can still disable Live Activities in Settings, so check `ActivityAuthorizationInfo().areActivitiesEnabled` and always have a fallback channel (regular notifications).

## Exercise

Design a Live Activity for a food-delivery order: it should show ETA and status on the Lock Screen and update as the order progresses, without requiring the app to stay open. Specify the `ContentState` shape, whether updates come from local scheduling or server push, how you handle the order being cancelled after the activity started, and what the widget shows if the backend stops sending updates for 30 minutes.
