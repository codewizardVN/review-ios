[English](./Day1_Swift_Core.md) | [Tiếng Việt](./Day1_Swift_Core.vi.md)

# Day 1: Swift Core

## Goal

Build a strong foundation in the Swift concepts that matter most for senior iOS interviews and real-world design decisions.

## Topics

- `struct` vs `class`
- Value semantics vs reference semantics
- ARC
- Retain cycles
- Protocol-oriented programming
- Generics
- Error handling
- Access control
- `any` vs `some`

## What You Should Be Able To Explain

- When `struct` is the right default and when `class` is necessary
- Why value semantics can reduce shared mutable state bugs
- How ARC works at a high level
- Where retain cycles usually appear in iOS codebases
- Why protocols are useful beyond abstraction alone
- How generics improve API design and type safety
- When to use `any` and when to use `some`

## 1. `struct` vs `class`

### Key Idea

In Swift, `struct` is usually the default choice because it gives value semantics, safer mutation, and fewer shared-state bugs. Use `class` when you need identity, shared mutable state, inheritance, or reference-based lifecycle behavior.

### Quick Comparison

- `struct`
  - Value type
  - Copied on assignment
  - Safer by default
  - No inheritance
- `class`
  - Reference type
  - Shared instance on assignment
  - Supports identity checks
  - Supports inheritance and deinitialization

### Example

```swift
struct UserProfile {
    var name: String
}

final class SessionManager {
    var token: String?
}
```

### Senior Take

Do not answer this as "struct is faster, class is slower". That is shallow and often wrong. The better answer is about semantics, ownership, and mutation behavior.

## 2. Value vs Reference Semantics

### Key Idea

Value types reduce accidental coupling. When one part of the system changes a value, another part does not silently observe the same mutation unless you explicitly model that behavior.

### Example

```swift
struct Counter {
    var value: Int
}

var a = Counter(value: 0)
var b = a
b.value = 10

print(a.value) // 0
print(b.value) // 10
```

With a reference type, both variables could point to the same object and mutate shared state.

### Senior Take

This matters in state management, reducers, view models, caching, and concurrency. A senior answer should connect semantics to system behavior.

## 3. ARC and Memory Management

### Key Idea

ARC automatically tracks strong references and releases objects when their reference count reaches zero.

### What Matters In Practice

- Strong references keep objects alive
- Weak references do not keep objects alive
- Unowned references assume the object still exists
- ARC is not a garbage collector

### Example

```swift
final class Owner {
    var child: Child?
}

final class Child {
    weak var owner: Owner?
}
```

### Senior Take

What matters is not memorizing keywords. It is knowing object ownership and lifecycle, especially across delegates, closures, async tasks, and view/controller relationships.

## 4. Retain Cycles

### Common Places They Happen

- Closures capturing `self`
- Delegate relationships without `weak`
- Long-lived callbacks
- Timer / notification / observer patterns
- Async work that strongly retains objects longer than expected

### Example

```swift
final class ProfileViewModel {
    var onUpdate: (() -> Void)?

    func bind() {
        onUpdate = { [weak self] in
            self?.reload()
        }
    }

    private func reload() {}
}
```

### Senior Take

Do not blindly write `[weak self]` everywhere. Explain why the capture exists, who owns whom, and whether `self` should actually stay alive for the operation.

## 5. Protocol-Oriented Programming

### Key Idea

Protocols help define behavior contracts and reduce coupling. They are especially useful for testability, composability, and API boundaries.

### Example

```swift
protocol UserRepository {
    func fetchUser(id: String) async throws -> User
}
```

### Good Senior Framing

- Protocols are helpful at boundaries
- Too many protocols can overcomplicate the codebase
- Protocols should exist for a real substitution or abstraction need

## 6. Generics

### Key Idea

Generics let you write reusable, type-safe APIs without falling back to weakly typed code.

### Example

```swift
struct APIResponse<T: Decodable>: Decodable {
    let data: T
}
```

### Senior Take

A good senior answer explains where generics improve API clarity and where generic-heavy design becomes hard to read and maintain.

## 7. Error Handling

### What To Review

- `throws`
- `do-catch`
- Typed domain errors
- Mapping low-level errors into user-meaningful errors

### Example

```swift
enum NetworkError: Error {
    case invalidResponse
    case unauthorized
    case timeout
}
```

### Senior Take

Avoid leaking raw infrastructure errors directly to the UI. Explain how errors are translated across layers.

## 8. Access Control

### What To Review

- `private`
- `fileprivate`
- `internal`
- `public`
- `open`

### Senior Take

Access control is about API boundaries and reducing misuse, not just hiding implementation details.

## 9. `any` vs `some`

### Key Idea

- `some Protocol` means the concrete type is hidden but fixed
- `any Protocol` means existential storage that can hold any conforming type

### Senior Take

You should understand this well enough to discuss API design, performance trade-offs, and when existential types are the better fit.

## Practice Questions

- Why does Apple generally encourage using `struct` heavily in Swift?
- What problem does a closure capture list solve?
- What does `mutating` mean for a `struct`?
- What is the difference between `any` and `some`?
- When should you use `weak` vs `unowned`?
- What makes a protocol useful instead of unnecessary abstraction?

## Mini Checklist

- Can you explain ownership clearly?
- Can you spot where shared mutable state might become risky?
- Can you identify likely retain cycle locations?
- Can you justify `struct` or `class` with trade-offs instead of rules?
- Can you explain how a Swift API stays type-safe and maintainable?

## Suggested Exercise

Write a small model layer with:

- One `struct` entity
- One `class` manager
- One protocol-based repository
- One generic API response wrapper
- One custom error enum

Then explain why each type was chosen.

## Senior Notes

- Do not answer with isolated definitions.
- Connect every concept to ownership, maintainability, testing, and system behavior.
- Strong senior answers usually include trade-offs, not absolutes.
