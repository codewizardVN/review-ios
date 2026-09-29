[English](./DependencyInjection.md) | [Tiếng Việt](./DependencyInjection.vi.md)

[← SwiftUI](./README.md)

# Dependency Injection in SwiftUI

## Key Idea

SwiftUI works best when dependencies are explicit. Views should receive the data and services they need through initializers, environment values, or owned state objects with clear ownership.

## Common Approaches

### Initializer injection

Good for explicit dependencies and easy previews. The view (or view model) receives dependencies as `init` parameters, so the signature tells you what it needs and the compiler catches a missing one. Downside: you have to pass it through every level if the dependency is needed deep down.

### Environment injection

Useful for cross-cutting app dependencies, but can become implicit if overused. An ancestor sets the value with `.environment(...)` (a custom key declared with `@Entry` in an `extension EnvironmentValues`, or an `@Observable` object by type), and descendants read it with `@Environment` without any parameter. Convenient, but the dependency doesn't appear in the view's signature.

### `@StateObject` ownership

Appropriate when the view creates and owns a view model that itself depends on services passed in. Typically written as `init(repository: UserRepository) { _viewModel = StateObject(wrappedValue: ProfileViewModel(repository: repository)) }` (or `_viewModel = State(initialValue: ...)` with `@Observable`); note the value is only used the first time for each view identity.

## Practice Questions

- When is `EnvironmentObject` helpful versus too magical?
- How do you keep SwiftUI previews easy to construct?

## Senior Take

The goal is not to eliminate all convenience. The goal is to keep ownership and dependency direction obvious enough that the view tree stays testable and predictable.

## Practice Question Answers

### When is `EnvironmentObject` helpful versus too magical?

`EnvironmentObject` is helpful when a dependency truly cuts across the app and lives for the app or scene — session, theme, feature flags, router — and it becomes too magical when used to pass one screen's own dependencies, so that nobody can look at a view and know what it needs.

Mechanism: an ancestor injects an object by type, and descendants read it back by type without any initializer parameter. That saves "drilling" a dependency through five or six levels of views, but in exchange:

- The view's signature doesn't reflect its dependencies, so previews, tests, and readers have to guess.
- A missing injection is a runtime crash, with no compile-time check.
- There is only one instance per type in a branch of the tree, which makes two parallel versions awkward.

Practical rule: if the dependency is needed on many unrelated screens and there is a single instance for the whole app, the environment is reasonable. If only `ProfileView` and its view model need `UserRepository`, pass it through the initializer. From iOS 17, `@Environment(Session.self)` with `@Observable` replaces `EnvironmentObject`, but the "should this go in the environment" question is answered by the same criteria.

### How do you keep SwiftUI previews easy to construct?

Keep previews easy to construct by routing every dependency through a protocol and passing it in from outside, so a preview needs one line of initialization with a mock instead of the whole app.

Specifically:

- Define `UserRepository` as a protocol; have a mock that returns sample data immediately.
- The view model receives the repository through `init`; the view receives the view model (or repository) through `init`.
- The view never reaches for `.shared` or a singleton inside `body`/`init`.
- Prepare sample data (`Profile.sample`) for loading, empty, and error states.

```swift
struct MockUserRepository: UserRepository {
    func fetchProfile() async throws -> Profile { .sample }
}

#Preview {
    ProfileView(viewModel: ProfileViewModel(repository: MockUserRepository()))
}
```

For dependencies coming through the environment, give the environment key a safe default (no-op or mock) rather than the real service, or use `PreviewModifier` (iOS 18+) to build a shared environment once for many previews. Trade-off: a protocol for everything adds boilerplate; only abstract dependencies with side effects (network, database, clock), not every simple struct.

## Interview Traps

### "Read a service from @Environment and pass it into @StateObject right in the view's init?"

**Common wrong answer:** Writing `init() { _viewModel = StateObject(wrappedValue: ProfileViewModel(repository: repository)) }` where `repository` is an `@Environment` property, and expecting it to work.

**Better answer:** `@Environment` values are only valid once the view is installed in the tree and `body` is running; in `init` they don't hold the right value yet (SwiftUI even logs a warning when environment is read outside a view). The right way: split out a wrapper view that reads the environment in `body` and passes it to the child's `init`, or configure the view model in `.task { viewModel.configure(repository) }`.

### "A static let shared singleton for the session is the simplest DI?"

**Common wrong answer:** Believing that calling `SessionManager.shared` from everywhere is acceptable, just "less pretty".

**Better answer:** A singleton hides the dependency: tests can't substitute it and previews hit the real service. In the Swift 6 language mode, `static let shared = SessionManager()` with a non-`Sendable` class that isn't isolated to an actor is also a compile error ("static property 'shared' is not concurrency-safe..."), forcing you to mark it `@MainActor`, make it an actor, or make the type `Sendable`. (New projects created with Xcode 26 usually enable `MainActor` default actor isolation, where types are implicitly `@MainActor` and this error doesn't appear — but the hidden-dependency problem remains.) You can keep a single instance at the composition root, but inject it rather than letting views reach for it.

### "An environment key's default value is a good place for the real service?"

**Common wrong answer:** Declaring `@Entry var userRepository: any UserRepository = LiveUserRepository()` so you don't have to inject at the root.

**Better answer:** The default is used whenever you forget to inject, so previews and tests silently call the real network, and the missing injection never surfaces (unlike `@EnvironmentObject`, a missing value here doesn't crash). Also, the `@Entry` macro generates the key's `defaultValue` as a static computed property (`static var defaultValue: Value { LiveUserRepository() }`), so whenever SwiftUI needs the default (no ancestor injected a value), the default expression may be evaluated again and create a new instance — for a reference type, different views may get different instances rather than the single shared instance you expected. Exactly how often SwiftUI reads the default isn't documented, so don't rely on it. Make the default a no-op or placeholder, and inject the live version once at the app root.

## Exercise

Design a `ProfileView` that depends on a `UserRepository`. Show one version using initializer injection into a view model and another using environment injection. Then explain which one you would prefer for a shared app-wide session dependency.
