[English](./PushNotifications.md) | [Tiếng Việt](./PushNotifications.vi.md)

[← UIKit and App Lifecycle](./README.md)

# Push Notifications

## Key Idea

APNs delivers a payload; the app decides what to do with it. Registration, authorization, and the payload contract with the backend matter as much as the UI that eventually shows the notification.

## What To Review

- Registration flow — `registerForRemoteNotifications()`, device token delivery, sending the token to your backend
- `UNUserNotificationCenter` — authorization request, `willPresent` (foreground) and `didReceive` (tap/action) delegate methods
- Notification categories and actions — custom action buttons on a notification (e.g., "Reply", "Mark as read")
- Silent/background push — `content-available: 1`, triggers `application(_:didReceiveRemoteNotification:fetchCompletionHandler:)` for background data refresh (requires Background Modes > Remote notifications), subject to system throttling
- Notification Service Extension — mutate payload before display (e.g., decrypt content, download and attach an image) within a ~30s budget
- Rich notifications — `UNNotificationContentExtension` for custom UI
- Provisional authorization (iOS 12+) — request authorization with the `.provisional` option: no prompt is shown, notifications are delivered quietly to Notification Center, and the user decides to keep or turn them off right from the notification
- Deep linking from a tap — routing the `userInfo` payload into the app's navigation, including when the app was cold-launched by the tap

## Example

```swift
func userNotificationCenter(
    _ center: UNUserNotificationCenter,
    didReceive response: UNNotificationResponse,
    withCompletionHandler completionHandler: @escaping () -> Void
) {
    let userInfo = response.notification.request.content.userInfo
    if let orderId = userInfo["orderId"] as? String {
        router.navigate(to: .orderDetail(id: orderId))
    }
    completionHandler()
}
```

## Practice Questions

- Why is silent push not reliable for time-critical background updates?
- How would you test the tap-to-navigate flow when the app is fully terminated?

## Senior Take

Two areas separate strong answers here: (1) treating the notification payload as a versioned contract with the backend — a schema change on either side without coordination silently drops navigation or crashes older app versions, and (2) understanding that silent push delivery is not guaranteed or timely — it is throttled by the system based on app usage patterns, battery, and network conditions, so it cannot be the sole mechanism for anything time-sensitive.

## Practice Question Answers

### Why is silent push not reliable for time-critical background updates?

Silent push is unreliable because iOS treats it as a "hint that an update would be nice", not a mandatory command. The system is free to delay it, coalesce it, or drop it entirely. A silent push (`content-available: 1`, header `apns-push-type: background`, `apns-priority: 5`) only wakes the app if the system decides it is reasonable.

Reasons it arrives late or not at all:

- **Throttling.** Apple advises sending no more than a few per hour. Send more and the system drops some, especially on low battery, in Low Power Mode, or when the user rarely opens the app.
- **The user force-quit the app.** If the user swiped the app away in the app switcher, silent pushes will not wake it until the user opens it again.
- **Coalescing while offline.** When the device has no connection, APNs keeps only the latest notification per app. Older ones are lost.
- **Short run time.** When woken, the app has only about 30 seconds to do its work and call the completion handler.

So for time-sensitive things like chat messages, send a visible alert push. If the content needs processing (decryption, image download), use a Notification Service Extension, since it runs for every alert push with `mutable-content: 1`. VoIP calls use PushKit together with CallKit, and real-time lock screen status uses Live Activity push updates. Silent push should only be used to make data "fresher" for the next app launch. When the app returns to the foreground it must still fetch on its own.

### How would you test the tap-to-navigate flow when the app is fully terminated?

The way to test it is to fully kill the app, send a real or simulated push, tap it, and have Xcode attach the debugger exactly when the app launches. The cold-launch case goes through a completely different code path than when the app is running, so it must be tested separately.

Practical steps:

1. In Xcode, go to Edit Scheme, Run, Info, and choose "Wait for the executable to be launched". Xcode waits and attaches when the system launches the app.
2. Send the push. On the simulator, use `xcrun simctl push booted <bundle-id> payload.apns` or drag an `.apns` file onto the simulator. On a device, send through the APNs sandbox using the debug device token.
3. Tap the notification, with a breakpoint in `userNotificationCenter(_:didReceive:withCompletionHandler:)`.

What to verify:

- `UNUserNotificationCenter.current().delegate` must be assigned before `application(_:didFinishLaunchingWithOptions:)` returns. Assign it later and `didReceive` is not called for the tap that launched the app.
- `router.navigate(to: .orderDetail(id: orderId))` in the example may run before the UI is built. The router needs to hold the route until the app is ready.

Extract parsing `userInfo` into a route as a pure function so you can unit test it with fake payloads, and test the cold launch manually or with a UI test. Trade-off: UI tests with real pushes are fragile, so keep them few and focused on the most important payloads.

## Interview Traps

### "The user swiped the app away. Will a silent push still wake it to sync?"

**Common wrong answer:** Yes, silent push is designed to run in the background, so it always wakes the app.

**Better answer:** No. When the user deliberately force-quits from the app switcher, iOS takes that as the user not wanting the app to run in the background. Silent push and background fetch will not launch the app until the user opens it again. Alert pushes are still displayed normally, and the Notification Service Extension still runs because it is a separate process. If the business needs the user to see the information for sure, send an alert push.

### "A push arrives while the app is open. Why is there no banner?"

**Common wrong answer:** Because APNs does not send pushes while the app is in the foreground.

**Better answer:** The push does arrive, but by default iOS does not show a banner while the app is in the foreground. You must implement `userNotificationCenter(_:willPresent:withCompletionHandler:)` and return the options you want to display. The `.alert` option has been deprecated since iOS 14, so use `.banner` and `.list`. This is also where you decide not to show a banner if the user is already viewing that exact conversation.

```swift
completionHandler([.banner, .list, .sound])
```

### "Can you fetch the device token once, store it, and use it forever?"

**Common wrong answer:** Yes, the token is tied to the device so it never changes; just send it to the server the first time.

**Better answer:** The token can change when the user reinstalls the app, restores from a backup onto a new device, or when the system reissues it. Sandbox tokens (debug builds) and production tokens (TestFlight, App Store) are also different. Call `registerForRemoteNotifications()` on every launch and send the token to the server when it differs from the stored value. The server must also remove tokens when APNs responds with errors like `410 Unregistered`.

## Exercise

Design the payload schema and routing logic for a chat app: a push notification should let the user tap to jump directly to a specific conversation, and a silent push should update an unread-count badge in the background. Specify the JSON payload for both, how you'd version the schema so old app versions don't crash on unknown fields, and what fallback happens if the target conversation was deleted server-side before the tap.
