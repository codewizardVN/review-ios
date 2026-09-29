[English](./BackgroundExecution.md) | [Tiếng Việt](./BackgroundExecution.vi.md)

[← UIKit and App Lifecycle](./README.md)

# Background Execution

## Key Idea

iOS gives an app a small, unpredictable amount of background time. The system — not your app — decides when your background task actually runs, so any design that assumes a guaranteed schedule is wrong.

## What To Review

- `beginBackgroundTask(withName:expirationHandler:)` — asks for a short extra period (usually about 30 seconds on current iOS, not guaranteed) to finish in-flight work after entering background; must always register an expiration handler and end the task explicitly
- `BGAppRefreshTask` — short, periodic background refresh (e.g., pre-fetch feed content); scheduled via `BGTaskScheduler`, no guaranteed interval; each run only gets a short budget, about 30 seconds, so it only suits light work
- `BGProcessingTask` — longer background maintenance (e.g., database cleanup, large re-index); allowed to run longer (possibly several minutes), can require power/network constraints (`requiresExternalPower`, `requiresNetworkConnectivity`), typically runs when the device is idle, for example overnight while charging
- Background URLSession — downloads/uploads that continue even if the app is suspended or terminated, resumed via `application(_:handleEventsForBackgroundURLSession:completionHandler:)`
- `BGContinuedProcessingTask` (iOS 26+) — for work the user explicitly starts while the app is in the foreground (for example a video export) that must keep running when the user leaves the app; the system shows progress in system UI, the app must update `progress`, and the user can cancel it
- Task registration timing — each identifier must be declared in `BGTaskSchedulerPermittedIdentifiers` in `Info.plist`, and the handler must be registered with `BGTaskScheduler.shared.register(forTaskWithIdentifier:using:launchHandler:)` before `application(_:didFinishLaunchingWithOptions:)` returns. Submitting a request can happen at any time
- System throttling factors — battery level, Low Power Mode, how often the user opens the app, device usage patterns; none of this is directly controllable
- Testing background tasks — simulating a `BGTaskScheduler` run via LLDB (`e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:...]`) since waiting for a real trigger isn't practical; similarly `_simulateExpirationForTaskWithIdentifier:` tests the expiration handler. Run it on a real device, because `BGTaskScheduler` does not work in the Simulator

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

## Practice Question Answers

### Why must you reschedule a `BGAppRefreshTask` at the start of its handler instead of the end?

You must reschedule at the start of the handler because the end may never be reached. If it is not reached, the refresh chain breaks and the app is not woken again until the user opens it. Each `BGAppRefreshTaskRequest` is single-use. Once the system runs it, it is gone and does not repeat, so for periodic refresh every run must schedule the next one itself.

There are many reasons the end of the handler may not run:

- The system runs out of time budget and calls `expirationHandler`. In the example, `FeedRefreshOperation` is cancelled, and the code after it may not run the way you expect.
- A network request hangs and its completion is never called.
- The app crashes or is killed for using too much memory in the background.

That is why the example calls `scheduleFeedRefresh()` on the very first line of `handleFeedRefresh(task:)`. Submitting a new request with the same identifier replaces the pending one, so you do not end up with duplicate schedules. You should also call `scheduleFeedRefresh()` when the app enters background, so there is always a first request scheduled.

Trade-off: `earliestBeginDate` only means "not earlier than this", not a schedule. Setting 15 minutes does not mean the app runs every 15 minutes. The system may run it hours later, or not at all for an app the user rarely opens.

### What's the difference in guarantees between a background URLSession upload and a `BGProcessingTask`?

A background URLSession guarantees the system will keep the transfer going until it finishes, even if the app is suspended or terminated by the system. A `BGProcessingTask` is only a request to "let me run sometime", which may run late or never.

The mechanisms differ in who does the work:

- **Background URLSession:** the app hands the transfer to a system process. That process uploads and retries when the network comes back, even though the app is no longer running. When it finishes, the system wakes or relaunches the app and calls `application(_:handleEventsForBackgroundURLSession:completionHandler:)` to deliver the result. Requirement: uploads must come from a file (`uploadTask(with:fromFile:)`); data tasks and the async `upload(for:from:)` do not work.
- **`BGProcessingTask`:** the code runs inside the app's own process, only when the system allows it (usually overnight, while charging if you set `requiresExternalPower`). It can be stopped at any moment through `expirationHandler`.

For the note-taking app in the exercise, the note upload should go through a background URLSession, while `BGProcessingTask` fits work like data cleanup or rebuilding an index. Trade-off: a background URLSession is not instant either. The system may defer transfers, especially with `isDiscretionary = true`, and if the user force-quits the app, pending transfers are cancelled.

### Why is `beginBackgroundTask` not a substitute for `BGTaskScheduler`?

Because `beginBackgroundTask` only extends run time right as the app enters background, while `BGTaskScheduler` is how the system wakes the app at a later time. The two APIs solve different problems.

`beginBackgroundTask(withName:expirationHandler:)` tells the system: "I am in the middle of this, don't suspend me yet". The app gets a short extra period, usually around 30 seconds on current iOS, but it is not guaranteed. Read `UIApplication.shared.backgroundTimeRemaining` instead of assuming a number. The app must call `endBackgroundTask` when the work is done, or at the latest in the `expirationHandler` before time runs out, or it gets killed. It cannot:

- Start new work three hours later.
- Wake an app that has been suspended or terminated.
- Run work lasting many minutes.

`BGTaskScheduler`, on the other hand, schedules the system to launch or wake the app later, with its own budget. In the exercise, `beginBackgroundTask` is for saving the note being edited and starting the upload right as the user leaves the app, while periodic catch-up sync is left to `BGTaskScheduler`. Since iOS 26 there is also `BGContinuedProcessingTask` for work the user explicitly started (like an export) that should keep running when the app goes to background. The request must be submitted while the app is in the foreground, the system shows progress based on the `progress` the app updates, and the user can cancel the task. It is not a way for the app to run in the background on a schedule. Trade-off: wrapping everything in `beginBackgroundTask` does not make the app run longer; it only makes the app more likely to be killed if you forget to end a task.

## Interview Traps

### "What if you forget to call endBackgroundTask? The system just stops it when time runs out, right?"

**Common wrong answer:** No problem; when time runs out, the system ends the task and suspends the app normally.

**Better answer:** If time runs out and the task has not been ended, the system kills the app instead of suspending it. The next time the user opens the app it is a cold launch and state is lost, and the crash log may show a reason related to the background task assertion. The `expirationHandler` must stop the work and call `endBackgroundTask(taskID)`, and the normal completion path must also call it exactly once. Wrap it in a helper so neither path forgets it or calls it twice.

### "Can you register a BGTaskScheduler handler anywhere, for example when the user turns on a sync setting?"

**Common wrong answer:** Yes, register whenever you need to, as long as it is before submitting the request.

**Better answer:** The handler must be registered before `application(_:didFinishLaunchingWithOptions:)` returns. When the system launches the app in the background to run a task, it needs to find the handler right at launch. Registering late throws an exception, and the identifier must also be listed in `BGTaskSchedulerPermittedIdentifiers` in Info.plist. The user's setting should only decide whether you submit a request; registration always happens at launch.

### "With earliestBeginDate set to 15 minutes, the feed refreshes every 15 minutes?"

**Common wrong answer:** Yes, that is the app's refresh frequency.

**Better answer:** `earliestBeginDate` is only the earliest point; the system picks the real time based on how often the user opens the app, battery, network, and Low Power Mode. A rarely used app may not run for days. If the user turns off Background App Refresh in Settings or force-quits the app, the task does not run. The UI must show something honest like "Last updated 3 hours ago", and the app must still refresh when it comes to the foreground.

## Exercise

Design the background strategy for a note-taking app that must sync locally-edited notes to a server. Specify: what work belongs in `beginBackgroundTask` versus `BGProcessingTask`, what happens if the sync task is killed mid-upload, how you avoid uploading the same note twice, and how the UI communicates "last synced" state honestly when background sync may not have run in hours.
