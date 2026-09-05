[English](./PushNotifications.md) | [Tiếng Việt](./PushNotifications.vi.md)

[← UIKit and App Lifecycle](./README.md)

# Push Notifications

## Key Idea

APNs delivers a payload; the app decides what to do with it. Registration, authorization, and the payload contract with the backend matter as much as the UI that eventually shows the notification.

## What To Review

- Registration flow — `registerForRemoteNotifications()`, device token delivery, sending the token to your backend
- `UNUserNotificationCenter` — authorization request, `willPresent` (foreground) and `didReceive` (tap/action) delegate methods
- Notification categories and actions — custom action buttons on a notification (e.g., "Reply", "Mark as read")
- Silent/background push — `content-available: 1`, triggers `application(_:didReceiveRemoteNotification:fetchCompletionHandler:)` for background data refresh, subject to system throttling
- Notification Service Extension — mutate payload before display (e.g., decrypt content, download and attach an image) within a ~30s budget
- Rich notifications — `UNNotificationContentExtension` for custom UI
- Provisional authorization — deliver quietly to Notification Center without a permission prompt
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
        router.navigate(to: .orderDetail(orderId))
    }
    completionHandler()
}
```

## Practice Questions

- Why is silent push not reliable for time-critical background updates?
- How would you test the tap-to-navigate flow when the app is fully terminated?

## Senior Take

Two areas separate strong answers here: (1) treating the notification payload as a versioned contract with the backend — a schema change on either side without coordination silently drops navigation or crashes older app versions, and (2) understanding that silent push delivery is not guaranteed or timely — it is throttled by the system based on app usage patterns, battery, and network conditions, so it cannot be the sole mechanism for anything time-sensitive.

## Exercise

Design the payload schema and routing logic for a chat app: a push notification should let the user tap to jump directly to a specific conversation, and a silent push should update an unread-count badge in the background. Specify the JSON payload for both, how you'd version the schema so old app versions don't crash on unknown fields, and what fallback happens if the target conversation was deleted server-side before the tap.
