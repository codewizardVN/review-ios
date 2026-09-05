[English](./Combine.md) | [Tiếng Việt](./Combine.vi.md)

[← Concurrency](./README.md)

# Combine

## Key Idea

Combine is Apple's reactive framework — `Publisher` emits values over time, `Subscriber` receives them, and operators transform the stream in between. `@Published` and `ObservableObject` in SwiftUI are built on top of it.

## What To Review

- `Publisher` / `Subscriber` / `Subscription` — the three core protocols
- Common operators — `map`, `flatMap`, `combineLatest`, `debounce`, `removeDuplicates`
- `@Published` — publishes a value change, backs most `ObservableObject` view models
- `AnyCancellable` — must be retained (usually in a `Set<AnyCancellable>`) or the subscription is torn down immediately
- Combine vs `async/await` — Combine models a *stream* of values over time; `async/await` models a single completion. Use Combine for continuous UI-driven state (search-as-you-type, form validation); use `async/await` for one-shot request/response work.

## Example

```swift
final class SearchViewModel: ObservableObject {
    @Published var query: String = ""
    @Published private(set) var results: [String] = []

    private var cancellables = Set<AnyCancellable>()

    init(searchService: SearchService) {
        $query
            .debounce(for: .milliseconds(300), scheduler: DispatchQueue.main)
            .removeDuplicates()
            .flatMap { query in searchService.search(query) }
            .receive(on: DispatchQueue.main)
            .assign(to: \.results, on: self)
            .store(in: &cancellables)
    }
}
```

## Practice Questions

- Why does forgetting to store a `Cancellable` cause a subscription to silently stop working?
- When would you still reach for Combine in a codebase that has fully adopted `async/await`?

## Senior Take

Combine is not dead just because `async/await` exists. `AsyncSequence` covers a lot of the same ground, but Combine's operator set (`debounce`, `combineLatest`, `removeDuplicates`) is still more mature for UI-driven, multi-source reactive state. Know both, and be able to justify which one fits a given data flow instead of defaulting to whichever is fashionable.

## Exercise

Build a `LoginFormViewModel` with `@Published var email: String` and `@Published var password: String`. Use `combineLatest` and `map` to derive a `@Published private(set) var isValid: Bool` that is true only when the email contains "@" and the password has 8+ characters. Wire it so a SwiftUI button's `disabled` state is bound to `!isValid`. Explain in a comment why this pattern would be awkward to express with plain `async/await`.
