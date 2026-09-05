[English](./InterviewQA.md) | [Tiếng Việt](./InterviewQA.vi.md)

[← Docs](./README.md) · [← Back to root](../README.md)

# Interview Q&A Set

Every question below is pulled directly from the "Practice Questions" (or, where a topic has none yet, the "Exercise") section of its topic file — nothing here was invented for this list. Use it as a rapid-fire drill after you've studied a day's topics in [PROGRESS.md](../PROGRESS.md): cover the answer, say it out loud with a trade-off, then check the source file if you get stuck.

## Day 1 — Swift Core

### [Value Types and Reference Types](../Swift/ValueTypes.md)
- How would you use a `BankAccount` type implemented as both a struct and a class to explain when copying a struct account versus assigning a class account changes the semantics of a `transfer(to:amount:)` call?

### [ARC and Memory Management](../Swift/ARC.md)
- How would you demonstrate a retain cycle caused by a `DataLoader`'s completion closure capturing `self` strongly, and why is `[weak self]` the right fix instead of `unowned`?

### [Protocol-Oriented Programming](../Swift/Protocols.md)
- Why does injecting an `AnalyticsService` protocol (with `FirebaseAnalytics` and `NoOpAnalytics` implementations) into a `CheckoutViewModel`'s initializer make the ViewModel testable?

### [Generics](../Swift/Generics.md)
- Why is the `Equatable` constraint necessary on an `EquatableStack`'s `contains(_:)` method that a plain generic `Stack<Element>` cannot support?

### [Opaque Types](../Swift/OpaqueTypes.md)
- Why does `some Shape` work for a factory function like `makeDefaultShape()` but `any Shape` become necessary for a function like `largestShape(from shapes: [any Shape])`?

### [Error Handling](../Swift/ErrorHandling.md)
- How does a full `do-catch` that handles each `ParseError` case (`missingField`, `invalidFormat`, `unsupportedVersion`) with a distinct user-facing message differ from just using `try?`?

### [Access Control](../Swift/AccessControl.md)
- How would you design a `KeychainStore` struct with the right access levels for its stored items, its public read/write methods, and its internal encrypt helper, and what would break if `items` were made public?

## Day 2 — Swift Concurrency

### [async/await](../Concurrency/AsyncAwait.md)
- After rewriting a completion-handler-based `fetchUser` function using async/await, in what real-world scenario would you still need to wrap it back into a completion-handler API with `withCheckedThrowingContinuation`?

### [Task and Cancellation](../Concurrency/Tasks.md)
- If the user leaves the screen, how should an in-flight request be handled?
- What is the difference between `Task.detached` and a regular `Task`?

### [Actor and MainActor](../Concurrency/Actors.md)
- When can bugs still happen even if you use `Actor`?

### [Structured Concurrency](../Concurrency/StructuredConcurrency.md)
- When is `async let` clearer for a `loadProfile()` function that fetches user, posts, and followers concurrently, and when does `withThrowingTaskGroup` become necessary instead?

### [Combine](../Concurrency/Combine.md)
- Why does forgetting to store a `Cancellable` cause a subscription to silently stop working?
- When would you still reach for Combine in a codebase that has fully adopted `async/await`?

### [Objective-C Interop](../Swift/ObjCInterop.md)
- Why would a `@objc` method marked `private` fail at runtime when called via `perform(_:)`?
- What happens if you forget `NS_ASSUME_NONNULL_BEGIN` in a legacy header a Swift module imports?
- Why can't a Swift `enum` with an associated value be exposed to Objective-C?

## Day 3 — SwiftUI

### [View Lifecycle](../SwiftUI/ViewLifecycle.md)
- Why is `.task` preferred over `onAppear` combined with manual task management for a `CountdownView` that must cancel its `Task.sleep`-based countdown when the user navigates away?

### [State Management](../SwiftUI/StateManagement.md)
- When should you use `@StateObject` instead of `@ObservedObject`?
- When is `EnvironmentObject` appropriate, and when is it overuse?

### [Navigation](../SwiftUI/Navigation.md)
- How would you pre-populate a `NavigationStack`'s `NavigationPath` on app launch so a deep link navigates directly to the Reviews screen for a specific item, skipping the List and Detail screens?

### [Rendering Performance](../SwiftUI/RenderingPerformance.md)
- Why does a view keep reloading unexpectedly?
- If a large list is laggy, where do you start debugging?

### [Dependency Injection in SwiftUI](../SwiftUI/DependencyInjection.md)
- When is `EnvironmentObject` helpful versus too magical?
- How do you keep SwiftUI previews easy to construct?

### [UIKit Interoperability](../SwiftUI/UIKitInterop.md)
- Why is a `Coordinator` needed when wrapping `UIColorPickerViewController` with `UIViewControllerRepresentable` to pass the selected `UIColor` back via a `@Binding<Color>`, and what is its lifecycle relative to the Representable?

### [Widgets and Live Activities](../SwiftUI/WidgetsLiveActivities.md)
- Why can't a widget just read the app's `@Observable` view model directly?
- What happens to a Live Activity's Lock Screen UI if push updates stop arriving?
- Why does the system limit how often `reloadTimelines` actually triggers a redraw?

## Day 4 — Architecture

### [MVC](../Architecture/MVC.md)
- After splitting a `ProductListViewController`'s `URLSession` call, inline price formatting, and detail-screen push into Model, Controller, and a separate Service, what becomes unit-testable and what remains untestable in UIKit MVC regardless?

### [MVVM](../Architecture/MVVM.md)
- How do you spot a ViewModel that is getting too big?
- What belongs in the ViewModel vs the use case layer?

### [Clean Architecture](../Architecture/CleanArchitecture.md)
- Should a small app use Clean Architecture?
- When does Clean Architecture become over-engineering?

### [Coordinator Pattern](../Architecture/Coordinator.md)
- When is Coordinator helpful, and when is it over-engineering?
- Should navigation decisions live in the ViewModel?

### [Dependency Injection](../Architecture/DependencyInjection.md)
- How does dependency injection help testing?
- What criteria would you use to decide between a DI container and manual injection?

### [Modularization](../Architecture/Modularization.md)
- What criteria would you use to split the first module?
- Whether module boundaries should be split by feature or by layer?

### [Design Patterns](../Architecture/DesignPatterns.md)
- Why does a `Repository` protocol matter more for testability than for the production implementation itself?
- When is a Singleton the right call, and when is it a sign that dependency injection was skipped?

## Day 5 — Networking, Persistence and Security

### [URLSession](../Networking/URLSession.md)
- Why does making `URLSession` injectable via init let you test a generic `APIClient`'s `fetch(_:from:)` with a `URLProtocol` stub for both valid JSON decoding and a non-200 `APIError.invalidResponse` case?

### [Codable](../Networking/Codable.md)
- What breaks if a domain `User` model decodes JSON directly instead of going through a `UserDTO` with `CodingKeys` mapping and a `toDomain()` conversion?

### [Request/Response Mapping](../Networking/RequestResponseMapping.md)
- When is it acceptable to skip DTOs?
- Where should mapping live: service, repository, or use case?

### [Pagination](../Networking/Pagination.md)
- Should pagination state live in the ViewModel or service?
- How do you avoid loading page 3 twice?

### [Retry / Timeout](../Networking/RetryTimeout.md)
- When does retry make sense and when does it not?
- How do you avoid duplicate requests when users interact quickly?

### [Cache Strategy](../Networking/CacheStrategy.md)
- Which layer should own caching?
- How do you avoid serving stale data after a logout?

### [Offline-First](../Networking/OfflineFirst.md)
- If the API is slow or unstable, how would you design the data flow?

### [Core Data](../Persistence/CoreData.md)
- Why must you never pass an `NSManagedObject` across threads directly?
- What happens if two contexts save conflicting changes to the same object?

### [SwiftData](../Persistence/SwiftData.md)
- What are the trade-offs of adopting SwiftData in an app that already has years of Core Data data?
- Why does `@Query` reduce the need for `NSFetchedResultsController`-style boilerplate?

### [Keychain](../Security/Keychain.md)
- Why would you choose `AfterFirstUnlock` over `WhenUnlocked` for a token needed by a background refresh task?
- What must you do explicitly so a token does not silently persist after the user deletes and reinstalls the app?

### [Network Security](../Security/NetworkSecurity.md)
- Why is pinning the public key generally preferred over pinning the leaf certificate?
- What is your rollback plan if a pinned key needs to change on short notice (e.g., a CA compromise)?

## Day 6 — Testing

### [Unit Tests](../Testing/UnitTests.md)
- Which tests should be written and which should not?
- If code is hard to test, where is the problem usually located?

### [UI Tests](../Testing/UITests.md)
- Which flows deserve UI tests first?
- How do you reduce flaky UI tests?

### [Mocking](../Testing/Mocking.md)
- How do mocks differ from stubs?
- Should you use a mocking framework or write fakes manually?

### [Testable Design](../Testing/TestableDesign.md)
- Should everything be tested?
- How much UI testing is enough without becoming flaky?

### [Snapshot Tests](../Testing/SnapshotTests.md)
- When do snapshot tests provide real value?

## Day 7 — Performance and Debugging

### [Main Thread Discipline](../Performance/MainThread.md)
- Why must a `SearchViewModel`'s JSON decoding and filtering move off the main thread with `Task.detached`, publishing the result back on `@MainActor` instead of doing it inline in `didReceiveData`?

### [Memory Leaks](../Performance/MemoryLeaks.md)
- If a view controller's `deinit` never fires after navigating away because of a `Timer` or `NotificationCenter` observer, how would you use the Memory Graph Debugger to find and fix the retain cycle?

### [Rendering Issues](../Performance/RenderingIssues.md)
- Why does the UI drop frames?
- Why can image loading make an app feel janky?

### [Startup Time](../Performance/StartupTime.md)
- After recording pre-main time with `DYLD_PRINT_STATISTICS=1` and identifying the three most expensive post-main operations in Instruments' App Launch tool, what concrete change would you propose for each?

### [Large List Optimization](../Performance/LargeListOptimization.md)
- If a screen scrolls poorly, what do you check first?

### [App Size Optimization](../Performance/AppSizeOptimization.md)
- Why can adding a single CocoaPod increase both binary size and app launch time?
- When would you use On-Demand Resources instead of bundling everything upfront?

## Day 8 — Senior Review and Interview Scenarios

### [System Design for iOS Apps](../Senior/SystemDesign.md)
- How do you split modules in a growing app?
- What would you simplify for a two-engineer team?

### [Code Review Mindset](../Senior/CodeReview.md)
- How do you review a large PR?
- How do you handle disagreement over an approach?

### [Refactoring Strategy](../Senior/Refactoring.md)
- When to refactor and when to leave the code as-is?
- How do you refactor a legacy codebase without breaking existing behavior?

### [Backward Compatibility](../Senior/BackwardCompatibility.md)
- How do you ship a new feature while supporting older app versions?
- When do you need a migration instead of a silent fallback?

### [Release Process](../Senior/ReleaseProcess.md)
- What blocks a release for you?
- How do you reduce release risk when the deadline is fixed?

### [CI/CD for Mobile](../Senior/CICD.md)
- How do you keep signing credentials in sync across a team without emailing `.p12` files around?
- What is your strategy when a CI build passes locally but fails in the pipeline?
- How would you speed up a 40-minute CI pipeline without cutting test coverage?

### [Debugging Production Issues](../Senior/ProductionDebugging.md)
- How do you approach a random production crash?

### [Technical Leadership](../Senior/TechnicalLeadership.md)
- If the team wants to ship quickly but code quality is poor, what do you do?
- If there is architectural disagreement, how do you handle it?
- How do you balance technical debt and product delivery?

## Day 9 — UIKit and App Lifecycle

### [App Lifecycle](../UIKit/AppLifecycle.md)
- What should happen when the app enters background?
- Where do you refresh critical state on returning to foreground?

### [View Controller Lifecycle](../UIKit/ViewControllerLifecycle.md)
- What is the difference between `viewWillAppear` and `viewDidAppear`?
- Which work should never happen in `viewDidLoad`?

### [Coordinator and Router](../UIKit/Coordinator.md)
- When should a screen trigger navigation directly?
- Who should respond to a deep link that opens a nested flow?

### [Auto Layout](../UIKit/AutoLayout.md)
- Why does a label get compressed unexpectedly?
- When should you use `UIStackView` and when not?

### [Collection View and Diffable Data Source](../UIKit/CollectionViewDiffable.md)
- Why can diffable still feel slow on large lists?
- What breaks if item identifiers are not stable?

### [Deep Links, Universal Links, and Notification Flows](../UIKit/DeepLinks.md)
- What happens if a deep link arrives before login finishes?
- Where should route parsing live?

### [Push Notifications](../UIKit/PushNotifications.md)
- Why is silent push not reliable for time-critical background updates?
- How would you test the tap-to-navigate flow when the app is fully terminated?

### [Background Execution](../UIKit/BackgroundExecution.md)
- Why must you reschedule a `BGAppRefreshTask` at the start of its handler instead of the end?
- What's the difference in guarantees between a background URLSession upload and a `BGProcessingTask`?
- Why is `beginBackgroundTask` not a substitute for `BGTaskScheduler`?

## Day 10 — Platform Quality and Growth

### [Accessibility](../Accessibility/Accessibility.md)
- Why is `accessibilityLabel("Heart icon")` on a favorite button a bad label?
- What breaks in a fixed-height cell design when a user sets the largest Dynamic Type size?
- Why does a custom-drawn chart (Canvas/Core Graphics) need explicit accessibility work that a native `List` gets for free?

### [Localization and Internationalization](../Accessibility/Localization.md)
- Why is `String(format: "%d items", count)` wrong for shipping to Arabic or Russian locales?
- What breaks in a UIKit layout built with `.left`/`.right` constraints when the app runs in Arabic?
- Why shouldn't a feature flag or analytics event ever be keyed off a localized string?

### [App Store Submission and Review](../Senior/AppStoreSubmission.md)
- Why does a demo account with 2FA enabled almost guarantee a rejection?
- Why is a privacy manifest omission an automated rejection rather than a human judgment call?
- When is it right to appeal a rejection versus just fixing the flagged issue?

### [Crash Reporting and Analytics](../Senior/CrashReportingAnalytics.md)
- Why does a missing dSYM matter more than a missing line of code comment?
- Why is "crash-free users" usually a better release gate than raw crash count?
- Why should analytics event names be reviewed like an API, not added ad hoc per feature?

### [Feature Flags and Experimentation](../Senior/FeatureFlagsExperimentation.md)
- Why is random-per-session variant assignment usually wrong for an A/B test?
- What should happen if the flag-fetch network call fails on cold launch?
- Why does a "temporary" release flag from six months ago count as tech debt?
