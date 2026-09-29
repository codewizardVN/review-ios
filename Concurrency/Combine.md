[English](./Combine.md) | [Tiếng Việt](./Combine.vi.md)

[← Concurrency](./README.md)

# Combine

## Key Idea

Combine is Apple's reactive framework — `Publisher` emits values over time, `Subscriber` receives them, and operators transform the stream in between. `@Published` and `ObservableObject` in SwiftUI are built on top of it.

## What To Review

- `Publisher` / `Subscriber` / `Subscription` — the three core protocols: a publisher describes a source of values (with `Output` and `Failure` types), a subscriber receives values, and the subscription is the link between them, through which the subscriber requests how many values it wants (back-pressure) and can `cancel()`.
- Common operators — `map`, `flatMap`, `switchToLatest`, `combineLatest`, `debounce`, `removeDuplicates`. `flatMap` keeps every inner publisher running; `map` + `switchToLatest` keeps only the newest publisher and cancels the old one.
- `@Published` — publishes a value change, backs most `ObservableObject` view models
- `AnyCancellable` — must be retained (usually in a `Set<AnyCancellable>`) or the subscription is torn down immediately
- Combine vs `async/await` — Combine models a *stream* of values over time; `async/await` models a single completion. Use Combine for continuous UI-driven state (search-as-you-type, form validation); use `async/await` for one-shot request/response work.

## Example

```swift
protocol SearchService {
    func search(_ query: String) -> AnyPublisher<[String], Never>
}

@MainActor
final class SearchViewModel: ObservableObject {
    @Published var query: String = ""
    @Published private(set) var results: [String] = []

    init(searchService: SearchService) {
        $query
            .debounce(for: .milliseconds(300), scheduler: DispatchQueue.main)
            .removeDuplicates()
            .map { query in searchService.search(query) } // each query -> one publisher
            .switchToLatest()                             // cancels the old request on a new query
            .receive(on: DispatchQueue.main)
            .assign(to: &$results)                        // no retain cycle, no store(in:) needed
    }
}
```

The two key choices in this example (`switchToLatest` instead of `flatMap`, `assign(to: &$results)` instead of `assign(to:on: self)`) are explained in Interview Traps.

## Practice Questions

- Why does forgetting to store a `Cancellable` cause a subscription to silently stop working?
- When would you still reach for Combine in a codebase that has fully adopted `async/await`?

## Senior Take

Combine is not dead just because `async/await` exists. `AsyncSequence` covers a lot of the same ground, but Combine's operator set (`debounce`, `combineLatest`, `removeDuplicates`) is still more mature for UI-driven, multi-source reactive state. Know both, and be able to justify which one fits a given data flow instead of defaulting to whichever is fashionable.

## Practice Question Answers

### Why does forgetting to store a `Cancellable` cause a subscription to silently stop working?

Because `AnyCancellable` calls `cancel()` in its `deinit`: if nobody holds it, it is released right after the statement and the subscription is torn down with it.

Mechanism: `sink` and `assign(to:on:)` return an `AnyCancellable` that represents the whole subscription chain. The chain lives only as long as someone holds a strong reference to that `AnyCancellable`. If you assign it to a local variable, or ignore the return value, then when the scope ends (often the end of `init`), ARC releases it, `cancel()` is called, and the publisher stops sending values. There's no error or crash, the UI just never updates, which makes it hard to debug. The compiler warns "result unused", but that's easy to miss.

This is by design: the subscription's lifetime is tied to the lifetime of the object that owns it. The usual pattern is to declare `private var cancellables = Set<AnyCancellable>()` in the view model and call `.store(in: &cancellables)`, so the subscription lives as long as the view model and is torn down automatically when the view model is released, with no manual cleanup. The exception is `assign(to: &$results)` as used in `SearchViewModel`: it returns no cancellable, because the subscription is attached directly to the `@Published` property and lives with it.

```swift
$query.sink { print($0) }                         // cancelled immediately (only prints the current value)
$query.sink { print($0) }.store(in: &cancellables) // lives with the view model
```

The opposite caution: storing a cancellable somewhere that lives longer than needed (for example a singleton) keeps the subscription and its closures alive too long.

### When would you still reach for Combine in a codebase that has fully adopted `async/await`?

Reach for Combine when the problem is a continuous stream of values that needs time-based operators or combines several sources, and when the frameworks you use still speak Combine.

Specifically:
- Time-based operators: `debounce`, `throttle` for search-as-you-type like `SearchViewModel`.
- Combining sources: `combineLatest` for form validation like `LoginFormViewModel` in the exercise, `merge` for several event streams.
- System APIs that return publishers: `NotificationCenter.publisher`, `Timer.publish`, KVO `publisher(for:)`, and `ObservableObject`/`@Published` for apps still supporting iOS below 17.

`async/await` models a single result. `AsyncSequence` models streams, but the standard library has no built-in `debounce` or `combineLatest`; you need the `swift-async-algorithms` package or write them yourself. The two worlds still connect: `publisher.values` (iOS 15+) turns a publisher into an `AsyncSequence` you can use with `for await`.

Trade-off: Combine has largely not been redesigned for Swift 6 strict concurrency (many publishers and operators aren't `Sendable`, and Combine knows nothing about actor isolation, so you often have to `receive(on:)` back to main yourself), and since iOS 17 `@Observable` replaces `ObservableObject` without using Combine. New code should keep Combine in small places that truly need its operators, rather than as the main architecture.

## Interview Traps

### "If `SearchViewModel` wrote `.assign(to: \.results, on: self).store(in: &cancellables)` instead of `.assign(to: &$results)`, would anything be wrong?"

**Common wrong answer:** "No, both are the same standard way to bind results to a property." The `on: self` form creates a retain cycle.

**Better answer:** `assign(to:on:)` holds a strong reference to the `on:` object, and the cancellable is stored in `self.cancellables`, so `self` holds the subscription and the subscription holds `self`; the view model is never released (and the subscription is never cancelled). That's why the example uses `assign(to: &$results)` (iOS 14+): it ties the lifetime to the `@Published` property itself, creates no cycle, and needs no `store(in:)`. If you need more complex logic, use `sink` with `[weak self]`.

### "If `SearchViewModel` used `flatMap` instead of `map` + `switchToLatest()`, would results always match the last query?"

**Common wrong answer:** "Yes, `debounce` already filters, so the displayed results are for the last query." `debounce` only reduces the number of requests; it doesn't cancel old ones.

**Better answer:** `flatMap` keeps every inner publisher alive, so the requests for "ab" and "abc" can run in parallel, and if "ab" returns later the UI shows stale results. That's why the example uses `map` to a publisher and then `switchToLatest()`: it cancels the previous publisher whenever a new value arrives, so only the newest query's results are assigned to `results`. This is the Combine version of the `task?.cancel()` pattern from the Task topic.

### "Inside `$query`'s `sink`, does reading `self.query` give the new value?"

**Common wrong answer:** "Yes, it only publishes after the property has changed." In fact `@Published` emits in `willSet`.

**Better answer:** `@Published` sends the new value **before** the property is assigned, so inside `sink`, `self.query` still holds the old value. Always use the value the closure receives instead of reading the property again. This bug often shows up when `sink` calls another method that reads several properties of the view model at once.

## Exercise

Build a `LoginFormViewModel` with `@Published var email: String` and `@Published var password: String`. Use `combineLatest` and `map` to derive a `@Published private(set) var isValid: Bool` that is true only when the email contains "@" and the password has 8+ characters. Assign the result with `assign(to: &$isValid)` to avoid a retain cycle. Wire it so a SwiftUI button's `disabled` state is bound to `!isValid`. Explain in a comment why this pattern would be awkward to express with plain `async/await`.
