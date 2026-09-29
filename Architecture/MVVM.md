[English](./MVVM.md) | [Tiếng Việt](./MVVM.vi.md)

[← Architecture](./README.md)

# MVVM (Model-View-ViewModel)

## Key Idea

The ViewModel holds presentation logic and exposes state the View binds to. The View is passive — it renders state and forwards events.

## Responsibilities

- **Model** — data, business rules, domain logic
- **ViewModel** — formats model data for display, handles user input, triggers use cases
- **View** — renders ViewModel output, forwards user actions

## Example

```swift
@MainActor
final class FeedViewModel: ObservableObject {
    @Published private(set) var items: [FeedItem] = []
    @Published private(set) var isLoading = false

    private let repository: FeedRepository

    init(repository: FeedRepository) {
        self.repository = repository
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        items = (try? await repository.fetchFeed()) ?? []
    }
}
```

The example above uses `ObservableObject` + `@Published` (Combine), which works on every iOS version SwiftUI supports. If the app targets iOS 17+, the modern approach is the `@Observable` macro (Observation framework): drop `ObservableObject` and `@Published`, views re-render only when they read the property that actually changed, and the view holds the ViewModel with `@State` instead of `@StateObject`. The MVVM structure (the ViewModel owns state, the repository is injected through `init`) stays the same.

## Practice Questions

- How do you spot a ViewModel that is getting too big?
- What belongs in the ViewModel vs the use case layer?

## Senior Take

MVVM does not automatically mean Clean Architecture. A ViewModel that talks directly to URLSession is still tightly coupled. Use MVVM for presentation logic; add a service/use case layer below it for business logic.

## Practice Question Answers

### How do you spot a ViewModel that is getting too big?

The clearest sign is when the ViewModel starts doing things other than "what this screen shows and how it reacts to input".

Concrete symptoms:

- `init` takes too many dependencies (five or six services or more), usually because the ViewModel is orchestrating a business flow itself.
- It contains business rules: computing discounts, checking whether an order can be placed, combining data from several repositories. These would have to be rewritten if another screen or a widget needed them.
- It calls `URLSession`, a database, or `UserDefaults` directly instead of going through a repository.
- It has many loose `Bool` flags such as `isLoading`, `isEmpty`, `hasError` that can contradict each other, instead of a single `enum State`.
- It serves several independent areas of the screen (header, list, filters) in one class.
- Its test file needs a very long setup just to check one small behaviour.

How to fix it: push business rules down into use cases/services, split child ViewModels per section, collapse state into an enum. The trade-off is not to count lines mechanically: a 300-line ViewModel that only handles presentation for one complex screen is fine. Splitting too early creates extra objects and bindings that are hard to follow.

### What belongs in the ViewModel vs the use case layer?

The ViewModel holds the presentation logic of one specific screen; the use case holds business rules that are true no matter what the UI looks like.

The ViewModel handles: formatting data for display (in the exercise, turning Kelvin into the string "23°C"), mapping errors into a readable `errorMessage`, managing `isLoading`, debouncing a search field, deciding which buttons are enabled. These are tied to one screen and change when the design changes.

The use case handles: business rules, for example "orders over 500k get free shipping", "show a heat warning above 35°C", combining several repositories, caching or retry policy. A simple check: if tomorrow the UI moves from UIKit to SwiftUI, or you add a widget and an App Intent, is this logic still needed? If yes, it belongs in a use case.

Trade-off: for a simple CRUD screen, the use case just forwards to the repository in one line, which is pure boilerplate. In that case letting the ViewModel call the repository directly is acceptable, and you extract a use case only when a real business rule appears or needs to be reused in several places.

## Interview Traps

### "`FeedViewModel` is `@MainActor`, so does `await repository.fetchFeed()` run on the main thread and freeze the UI?"

**Common wrong answer:** "Yes, everything in a `@MainActor` class runs on the main thread, so you must wrap networking in `Task.detached`."

**Better answer:** `await` is a suspension point: while waiting, the main actor is freed to do other work, so the UI is not blocked. Where the code inside `fetchFeed()` runs depends on that function's own isolation, not the caller's; `URLSession` does its I/O off the main thread anyway. Version note: from Swift 6.2, with `NonisolatedNonsendingByDefault` enabled (new projects created with Xcode 26 usually turn it on through the "Approachable Concurrency" build setting), `nonisolated` async functions run on the caller's actor, so CPU-heavy work (decoding a large JSON) should be marked `@concurrent` to run off the main actor. `Task.detached` is rarely the right answer.

### "In SwiftUI, is it a problem to create the ViewModel in the view with `@ObservedObject var vm = FeedViewModel(...)`?"

**Common wrong answer:** "No, `@ObservedObject` and `@StateObject` are basically the same."

**Better answer:** `@ObservedObject` does not own the object: every time the parent re-renders and recreates the view struct, a new ViewModel is created, and state and running tasks are lost. An object the view creates itself must use `@StateObject`; with `@Observable` (iOS 17+) use `@State`. Small gotcha: with `@State var vm = FeedViewModel()`, the initializer still runs every time the view struct is re-created (SwiftUI keeps only the first instance), so don't put side effects in the ViewModel's `init`.

### "What's wrong with `items = (try? await repository.fetchFeed()) ?? []`?"

**Common wrong answer:** "Nothing, it's concise and safe because it never crashes."

**Better answer:** `try?` swallows the error: a network failure and "the feed really is empty" look identical to the user and to tests. You can't show an error message or a retry button, and tests can't tell the two cases apart. Use `do/catch` and set an error state, or model it as `enum State { case loading, loaded([FeedItem]), failed(String) }`. If the task is cancelled, ignore `CancellationError` instead of showing it as an error.

## Exercise

Build a `WeatherViewModel` with `@Published var temperature: String`, `@Published var isLoading: Bool`, and `@Published var errorMessage: String?`. Inject a `WeatherService` protocol that returns raw Kelvin. The ViewModel converts Kelvin to "23°C" format. Write a `FakeWeatherService`. Write 3 unit tests: success (correct format), service error (errorMessage set), and verify no UIKit import in the ViewModel file.
