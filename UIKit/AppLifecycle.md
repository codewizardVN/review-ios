[English](./AppLifecycle.md) | [Tiếng Việt](./AppLifecycle.vi.md)

[← UIKit and App Lifecycle](./README.md)

# App Lifecycle

## Key Idea

App lifecycle events tell you when the app launches, becomes active, goes to background, and returns to foreground. These transitions are where persistence, refresh, analytics, and security behavior often live.

## What To Review

- `UIApplicationDelegate` responsibilities: process-level work that happens once for the whole app, such as configuring services (crash reporting, analytics), registering `BGTaskScheduler` handlers, assigning `UNUserNotificationCenter.current().delegate`, receiving the push device token, and `applicationWillTerminate`. Once the app uses scenes, the AppDelegate no longer owns UI and no longer receives foreground/background events.
- Scene-based lifecycle with `UISceneDelegate` (in practice `UIWindowSceneDelegate`): each scene is one UI "window" of the app (on iPad there can be several at once). The scene delegate creates the window in `scene(_:willConnectTo:options:)` and receives `sceneWillEnterForeground`, `sceneDidBecomeActive`, `sceneWillResignActive`, `sceneDidEnterBackground`, and `sceneDidDisconnect`.
- Foreground/background transitions: the app moves through not running → inactive → active (receiving interaction) → inactive → background (still running code for a short time) → suspended (in memory but not running code). From suspended, the system can kill the app at any time without notice.
- What should and should not happen on launch: `application(_:didFinishLaunchingWithOptions:)` and `scene(_:willConnectTo:options:)` are on the startup path, so only do what is needed to show the first screen plus the things that must happen at launch (registering background tasks, assigning the notification delegate, reading the URL/notification that opened the app). Heavy or non-urgent work (fetching config, cleaning caches, initializing secondary SDKs) should wait until the first UI is on screen, or run lazily when needed.

## Practice Questions

- What should happen when the app enters background?
- Where do you refresh critical state on returning to foreground?

## Senior Take

Lifecycle code should stay thin. The delegate layer coordinates app-level services, but feature logic should remain in dedicated objects so the app is testable and maintainable.

## Practice Question Answers

### What should happen when the app enters background?

When the app enters background, the main job is to save whatever the user has not saved yet, stop expensive work, and hide sensitive content, all of it fast. For scene-based apps the callback is `sceneDidEnterBackground(_:)`. For older AppDelegate-only apps it is `applicationDidEnterBackground(_:)`. The callback must return quickly (Apple says about 5 seconds; take too long and the app may be killed), and after it returns the app is suspended soon unless it asks for more time. Once suspended, all of the app's threads are frozen; they do not keep running as usual.

What to do:

- Save drafts, in-progress forms, and reading position. If you use state restoration, return an `NSUserActivity` from `stateRestorationActivity(for:)`.
- Stop timers, animations, and unnecessary location updates, and pause video.
- Cover sensitive screens (balances, OTP codes) before the system takes the app switcher snapshot. Doing this in `sceneWillResignActive(_:)` makes sure it happens in time.
- Schedule a `BGAppRefreshTask` if you need a refresh later.

If something needs more time (for example an in-flight upload), wrap it in `beginBackgroundTask` rather than blocking the callback. Trade-off: do not pile feature logic into the SceneDelegate. Each service should listen to `UIScene.didEnterBackgroundNotification` itself, or be called by a lifecycle coordinator, so the delegate stays thin.

### Where do you refresh critical state on returning to foreground?

Usually refresh in `sceneWillEnterForeground(_:)`, when the app is about to be shown to the user again. Work that should only happen once the app is truly receiving interaction belongs in `sceneDidBecomeActive(_:)`. The two callbacks differ in how often they fire. `willEnterForeground` only runs when coming up from background. `didBecomeActive` also runs when the user pulls down Control Center and lets go, or when a system alert or Face ID prompt closes. A heavy API call in `didBecomeActive` gets triggered far too often.

"Critical" state usually means:

- Whether the session token is still valid. If it has expired, ask the user to log in again before showing data.
- System permissions the user may have changed in Settings (notifications, location, camera).
- Time-sensitive data: badges, balances, feeds.

A good approach is to have the SceneDelegate only broadcast "the app came back to the foreground". A `SessionManager`, or each feature, decides whether a refresh is needed based on when it last refreshed (for example only if more than 5 minutes have passed). Trade-off: refreshing everything on every return is safe but costs battery and makes the UI flicker. Throttle it and prioritize what the user sees first.

## Interview Traps

### "Does the code in AppDelegate's applicationDidEnterBackground run?"

**Common wrong answer:** Yes, the AppDelegate always receives every foreground/background event; the SceneDelegate is just an add-on.

**Better answer:** Once the app has adopted scenes (a `UIApplicationSceneManifest` in Info.plist), UIKit calls `sceneDidEnterBackground`, `sceneWillEnterForeground`, and so on, on the SceneDelegate. The matching AppDelegate methods are no longer called. App-level notifications like `UIApplication.didEnterBackgroundNotification` are still posted, so services that listen to notifications keep working. At WWDC25 (TN3187) Apple also announced: with the iOS 26 SDK, an app that has not adopted the scene lifecycle only gets a logged warning; but starting with the major iOS release after iOS 26, a UIKit app built with the latest SDK that has not adopted the scene lifecycle will fail to launch. The requirement is tied to building with the latest SDK, not only to the iOS version the user is running. So new lifecycle code should be written for scenes.

### "Is it fine to refresh data in didBecomeActive?"

**Common wrong answer:** Yes, because `didBecomeActive` means "the app just came back from background".

**Better answer:** `didBecomeActive` fires every time an interruption ends: after closing Control Center or Notification Center, a permission alert, a Face ID prompt, or an incoming call. In none of these cases did the app enter background. Putting a network refresh here causes extra requests, or even a loop: the Face ID prompt makes the app resign active, then it becomes active again, which triggers Face ID again. A "user came back to the app" refresh belongs in `sceneWillEnterForeground`. `didBecomeActive` is for things like resuming a game, the camera, or animations.

### "Saving data in applicationWillTerminate is enough, right?"

**Common wrong answer:** Yes, `applicationWillTerminate` (or `sceneDidDisconnect`) is the last chance to save before the app shuts down.

**Better answer:** Most of the time the app "dies" while it is suspended: the system reclaims memory, or the user swipes it away. The process is then killed with no callback at all. `applicationWillTerminate` almost only runs when the app is executing in the background and has not yet been suspended. `sceneDidDisconnect` does not mean the app is terminating either: the system may disconnect a scene to reclaim resources and reconnect it later. Save in `sceneDidEnterBackground`, or as soon as the data changes.

## Exercise

List the actions your app should take on cold launch, when moving to background, and when returning to foreground. Then identify which of those actions are app-level orchestration versus feature-level behavior.
