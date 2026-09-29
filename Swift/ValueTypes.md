[English](./ValueTypes.md) | [Tiếng Việt](./ValueTypes.vi.md)

[← Swift Core](./README.md)

# Value Types and Reference Types

## 1. `struct` vs `class`

### Key Idea

In Swift, `struct` is usually the default choice because it gives value semantics, safer mutation, and fewer shared-state bugs. Use `class` when you need identity, shared mutable state, inheritance, or reference-based lifecycle behavior.

### Quick Comparison

- `struct`
  - Value type
  - Copied on assignment or when passed to a function (semantically; types like `Array` and `String` use copy-on-write, so the data is only physically copied on mutation)
  - Safer by default: each variable holds its own copy, and mutation requires a `var` and a `mutating` method
  - No inheritance (use protocols to share behavior)
- `class`
  - Reference type
  - Shared instance on assignment: both variables point to the same object, so a change through one is visible through the other
  - Supports identity checks with `===` (do two variables point to the same object?)
  - Supports inheritance and `deinit` (ordinary structs/enums have no `deinit`; only `~Copyable` structs/enums, since Swift 5.9, can declare one)

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

## Practice Question Answers

### How would you use a BankAccount type implemented as both a struct and a class to explain when copying a struct account versus assigning a class account changes the semantics of a transfer(to:amount:) call?

I would show that with a struct, `var copy = account` creates an independent account, so a transfer on the copy never touches the original; with a class, `let alias = account` only adds another reference to the same object, so a transfer through `alias` changes a balance that everyone holding that reference can see.

The mechanism shows up in the method signature. The struct version must be `mutating` and the receiving account must be `inout`, so the call site carries an `&` — the reader immediately knows which values change. The class version mutates both objects with no visible sign at the call site.

```swift
struct AccountValue {
    var balance: Decimal
    mutating func transfer(to other: inout AccountValue, amount: Decimal) {
        balance -= amount; other.balance += amount
    }
}
var a = AccountValue(balance: 100), b = AccountValue(balance: 0)
var snapshot = a
a.transfer(to: &b, amount: 30)   // snapshot.balance is still 100
```

Trade-off: a real bank account has identity (it has an ID, it is one unique entity), so if several screens must see the same changing balance, a class — or better, an `actor` once concurrency is involved — models the domain more honestly. A struct fits snapshots (the balance at one moment, data returned from the server), where accidentally shared state is a bug rather than a feature.

## Interview Traps

### "Structs always live on the stack, so they are always faster than classes, right?"

**Common wrong answer:** Agreeing that structs are always stack-allocated and classes heap-allocated, so switching to a struct always makes things faster.

**Better answer:** Storage location is an implementation detail. A struct ends up on the heap when it is an element of an `Array`, a property of a class, captured by an escaping closure, or too large for the inline buffer of an `any P` existential. A struct holding many `String`/`Array`/class references must retain/release each field when copied, which can cost more than passing one reference. Choose by semantics, then measure with Instruments if performance is in doubt.

### "Does assigning an Array of one million elements to another variable copy all the data?"

**Common wrong answer:** Yes, because Array is a value type so every assignment copies everything; or the opposite, that every struct automatically gets copy-on-write.

**Better answer:** `Array`, `Dictionary`, `Set`, `String` and `Data` use copy-on-write: assignment only bumps the reference count of the internal buffer, and the data is actually copied only when one side mutates while the buffer is not uniquely referenced. A struct you write yourself does not get COW for free — it only benefits from COW in stored properties of those types. To give your own type COW, you wrap a class storage and check `isKnownUniquelyReferenced(&storage)` before mutating.

### "A struct with a class-typed property still has value semantics, doesn't it?"

**Common wrong answer:** Yes, because anything declared as `struct` is independent when copied.

**Better answer:** No. Copying the struct only copies the reference held in the class-typed property, so both copies still point to the same object and mutations on it are shared — even if the struct is declared with `let`. Value semantics is a property of the whole data tree, not of the `struct` keyword. This is also why such a struct is not automatically `Sendable` in Swift 6 when the inner class is not `Sendable`.

## Exercise

Implement a `BankAccount` type first as a `struct`, then as a `class`. Add a `transfer(to:amount:)` method that moves funds between accounts. Observe what happens when you copy a struct account vs assign a class account and call transfer. Write 3 sentences explaining when each choice makes semantic sense for this domain.
