[English](./ValueTypes.md) | [Tiếng Việt](./ValueTypes.vi.md)

[← Swift Core](./README.md)

# Value Types and Reference Types

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

---

## 2. Value Semantics vs Reference Semantics

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

## Practice Questions

- How would you use a BankAccount type implemented as both a struct and a class to explain when copying a struct account versus assigning a class account changes the semantics of a transfer(to:amount:) call?

## Exercise

Implement a `BankAccount` type first as a `struct`, then as a `class`. Add a `transfer(to:amount:)` method that moves funds between accounts. Observe what happens when you copy a struct account vs assign a class account and call transfer. Write 3 sentences explaining when each choice makes semantic sense for this domain.
