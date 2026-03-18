[English](./CleanArchitecture.md) | [Tiếng Việt](./CleanArchitecture.vi.md)

[← Architecture](./README.md)

# Clean Architecture

## Key Idea

Organizes code into concentric layers where dependencies only point inward. Inner layers know nothing about outer layers.

## Layers (outer → inner)

1. **Presentation** — ViewModels, Views, UI logic
2. **Domain** — Use Cases, Entities, Repository protocols
3. **Data** — Repository implementations, API clients, local storage

## The Dependency Rule

The domain layer must not import UIKit, Foundation networking, or any framework. It only defines protocols that outer layers implement.

```text
Presentation → Domain ← Data
```

## Example

```swift
// Domain layer — pure Swift, no UIKit
protocol UserRepository {
    func fetchUser(id: String) async throws -> User
}

struct FetchUserUseCase {
    let repository: UserRepository
    func execute(id: String) async throws -> User {
        try await repository.fetchUser(id: id)
    }
}

// Data layer — implements the protocol
final class RemoteUserRepository: UserRepository {
    func fetchUser(id: String) async throws -> User { ... }
}
```

## Practice Questions

- Should a small app use Clean Architecture?
- When does Clean Architecture become over-engineering?

## Senior Take

Clean Architecture's value is in testability and replaceability — you can swap the data layer without touching the domain. The cost is boilerplate and indirection. It pays off in large teams, complex domains, or apps that need to be tested heavily.

## Exercise

Implement a "Get article list" feature in 3 layers: (1) Domain: `Article` entity, `ArticleRepository` protocol, `GetArticlesUseCase`. (2) Data: `RemoteArticleRepository` calling a mock URLSession. (3) Presentation: `ArticleListViewModel` using `GetArticlesUseCase`. Wire them in a unit test — no real network. Verify the domain layer has zero UIKit or networking imports.
