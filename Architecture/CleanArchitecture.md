[English](./CleanArchitecture.md) | [Tiếng Việt](./CleanArchitecture.vi.md)

[← Architecture](./README.md)

# Clean Architecture

## Key Idea

Organizes code into concentric layers where dependencies only point inward. Inner layers know nothing about outer layers.

## Layers (outer → inner)

1. **Presentation** — ViewModels, Views, UI logic
2. **Domain** — Use Cases, Entities, Repository protocols
3. **Data** — Repository implementations, API clients, local storage

Note: this list is not three nested rings in order. Domain is the innermost layer; Presentation and Data are both outer layers, sitting on either side and both pointing at Domain (see the diagram below).

## The Dependency Rule

The domain layer must not depend on volatile details: UIKit/SwiftUI, networking (`URLSession`), storage frameworks (Core Data, SwiftData), or third-party SDKs. Using foundational Foundation value types like `Date`, `UUID`, `Decimal` is normal (see Interview Traps). The domain only defines entities, use cases, and protocols; outer layers implement those protocols.

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

## Practice Question Answers

### Should a small app use Clean Architecture?

Usually it shouldn't build the full three layers with a use case for every action, but it should keep the core idea: dependencies point inward, and there is a protocol at the boundary with networking and the database.

Clean Architecture's value comes from isolating business logic from details that change often (APIs, storage frameworks, UI). A small app usually has very little business logic: mostly it fetches data from a server and shows it. Then `FetchUserUseCase` just forwards to `repository.fetchUser(id:)`, and the DTO, Entity, and display model are nearly identical. You pay the cost (more files, more mappers, more protocols) and get nothing back.

A practical approach for a small app: MVVM plus a repository protocol such as `UserRepository`. That is already enough to fake data in tests and previews. When a real business rule appears, or logic needs to be reused across several screens, that is the time to add a use case.

Exceptions: an app that is small but has a complex, long-lived domain (interest calculation, insurance, healthcare), or a team that knows the app will grow fast and needs a shared standard from the start. Then investing early is reasonable.

### When does Clean Architecture become over-engineering?

It becomes over-engineering when the intermediate layers buy nothing: no extra testability, no replaceability, no help with teams working in parallel.

Concrete signs:

- A use case is a one-line forward to the repository, and almost every use case looks like that.
- Three identical models (DTO, Entity, UI model) with mappers that just copy fields.
- Adding one displayed field means editing six or seven files across every layer.
- Every use case has its own protocol just for mocking, even though tests could use the real use case with a fake repository.
- Each layer is its own module in a five-screen app.
- A new team member needs days just to understand where a simple flow goes.

Rule of thumb: every layer of indirection must answer "which change does it protect me from?". If it can't, collapse layers but keep the dependency rule, for example a ViewModel calling the repository protocol directly. You keep testability and drop most of the boilerplate.

## Interview Traps

### "Can the domain layer `import Foundation`?"

**Common wrong answer:** "No, the domain must be absolutely pure Swift, no `Date`, `URL`, or `Decimal`." This reading makes teams re-implement basic types for no benefit.

**Better answer:** The dependency rule is about avoiding dependencies on volatile details: `URLSession`, Core Data, `UIImage`, third-party SDKs. Foundation value types like `Date`, `UUID`, `Decimal` are stable foundations and normal to use in the domain. Because `import Foundation` on Apple platforms also exposes `URLSession`, the compiler can't block it for you; to really enforce it, put the domain in its own target/module that doesn't depend on the networking module.

### "`Presentation → Domain ← Data` means data flows from Data into Domain, right?"

**Common wrong answer:** Confusing the source-code dependency direction with the runtime control flow.

**Better answer:** At runtime the call goes Presentation → use case → `RemoteUserRepository` (Data layer). But in source code, Data depends on Domain because it implements the `UserRepository` protocol that Domain defines. This is Dependency Inversion: Domain owns the interface, outer layers provide the implementation. Wiring concrete types to protocols happens at the composition root (the app target or `SceneDelegate`).

### "`FetchUserUseCase` is a struct, so it's automatically `Sendable` and can be passed across actors freely?"

**Common wrong answer:** "Structs are value types, so they're always safe under concurrency."

**Better answer:** A struct is only inferred `Sendable` when all its stored properties are `Sendable`, and that implicit inference only applies to non-`public` structs (a `public` struct must declare `: Sendable` itself, except `@frozen` structs). Here `repository` is `any UserRepository`, which is not `Sendable` unless the protocol is declared `protocol UserRepository: Sendable`. Under Swift 6 strict concurrency, sharing this use case across an isolation boundary produces an error, for example capturing it in a `Task` and still using it outside, or passing it to another actor. Region-based isolation (SE-0414, Swift 6) only lets you "transfer" a non-`Sendable` value when the sender no longer uses it, so don't rely on that for a shared dependency. The fix is to make the protocol refine `Sendable` and ensure implementations are actually safe (immutable, an actor, or lock-protected).

## Exercise

Implement a "Get article list" feature in 3 layers: (1) Domain: `Article` entity, `ArticleRepository` protocol, `GetArticlesUseCase`. (2) Data: `RemoteArticleRepository` calling URLSession, stubbed in tests with a custom `URLProtocol` (or by injecting an `HTTPClient` protocol). (3) Presentation: `ArticleListViewModel` using `GetArticlesUseCase`. Wire them in a unit test — no real network. Verify the domain layer has zero UIKit or networking imports.
