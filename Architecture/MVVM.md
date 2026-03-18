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

## Practice Questions

- How do you spot a ViewModel that is getting too big?
- What belongs in the ViewModel vs the use case layer?

## Senior Take

MVVM does not automatically mean Clean Architecture. A ViewModel that talks directly to URLSession is still tightly coupled. Use MVVM for presentation logic; add a service/use case layer below it for business logic.

## Exercise

Build a `WeatherViewModel` with `@Published var temperature: String`, `@Published var isLoading: Bool`, and `@Published var errorMessage: String?`. Inject a `WeatherService` protocol that returns raw Kelvin. The ViewModel converts Kelvin to "23°C" format. Write a `FakeWeatherService`. Write 3 unit tests: success (correct format), service error (errorMessage set), and verify no UIKit import in the ViewModel file.
