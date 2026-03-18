[English](./DependencyInjection.md) | [Tiếng Việt](./DependencyInjection.vi.md)

[← SwiftUI](./README.md)

# Dependency Injection in SwiftUI

## Key Idea

SwiftUI works best when dependencies are explicit. Views should receive the data and services they need through initializers, environment values, or owned state objects with clear ownership.

## Common Approaches

### Initializer injection

Good for explicit dependencies and easy previews.

### Environment injection

Useful for cross-cutting app dependencies, but can become implicit if overused.

### `@StateObject` ownership

Appropriate when the view creates and owns a view model that itself depends on services passed in.

## Practice Questions

- When is `EnvironmentObject` helpful versus too magical?
- How do you keep SwiftUI previews easy to construct?

## Senior Take

The goal is not to eliminate all convenience. The goal is to keep ownership and dependency direction obvious enough that the view tree stays testable and predictable.

## Exercise

Design a `ProfileView` that depends on a `UserRepository`. Show one version using initializer injection into a view model and another using environment injection. Then explain which one you would prefer for a shared app-wide session dependency.
