[English](./BackgroundExecution.md) | [Tiếng Việt](./BackgroundExecution.vi.md)

[← UIKit and App Lifecycle](./README.md)

# Background Execution

## Key Idea

iOS gives an app a small, unpredictable amount of background time. The system — not your app — decides when your background task actually runs, so any design that assumes a guaranteed schedule is wrong.

## What To Review

- `beginBackgroundTask(withName:expirationHandler:)` — buys a few extra seconds/minutes to finish in-flight work after entering background; must always register an expiration handler and end the task explicitly
- `BGAppRefreshTask` — short, periodic background refresh (e.g., pre-fetch feed content); scheduled via `BGTaskScheduler`, no guaranteed interval, budget is minutes not less
- `BGProcessingTask` — longer background maintenance (e.g., database cleanup, large re-index); can require power/network constraints, typically runs overnight while charging
- Background URLSession — downloads/uploads that continue even if the app is suspended or terminated, resumed via `application(_:handleEventsForBackgroundURLSession:completionHandler:)`
- Task registration timing — `BGTaskScheduler` identifiers must be registered in `Info.plist` and requested for execution before `applicationDidFinishLaunching` returns
- System throttling factors — battery level, Low Power Mode, how often the user opens the app, device usage patterns; none of this is directly controllable
- Testing background tasks — simulating a `BGTaskScheduler` run via LLDB (`e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:...]`) since waiting for a real trigger isn't practical

## Example

```swift
func scheduleFeedRefresh() {
    let request = BGAppRefreshTaskRequest(identifier: "com.app.feed.refresh")
    request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)
    try? BGTaskScheduler.shared.submit(request)
}

func handleFeedRefresh(task: BGAppRefreshTask) {
    scheduleFeedRefresh() // always reschedule the next one first
    let operation = FeedRefreshOperation()
    task.expirationHandler = { operation.cancel() }
    operation.completionBlock = { task.setTaskCompleted(success: !operation.isCancelled) }
    OperationQueue().addOperation(operation)
}
```

## Practice Questions

- Why must you reschedule a `BGAppRefreshTask` at the start of its handler instead of the end?
- What's the difference in guarantees between a background URLSession upload and a `BGProcessingTask`?
- Why is `beginBackgroundTask` not a substitute for `BGTaskScheduler`?

## Senior Take

The interview trap here is designing as if background execution is reliable. A strong answer treats background time as opportunistic and best-effort: the app must remain fully correct if the background task never runs at all, and background work exists purely to make the *next foreground launch* faster or fresher — never to guarantee a side effect happened.

## Exercise

Design the background strategy for a note-taking app that must sync locally-edited notes to a server. Specify: what work belongs in `beginBackgroundTask` versus `BGProcessingTask`, what happens if the sync task is killed mid-upload, how you avoid uploading the same note twice, and how the UI communicates "last synced" state honestly when background sync may not have run in hours.
