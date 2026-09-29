[English](./Generics.md) | [Tiếng Việt](./Generics.vi.md)

[← Swift Core](./README.md)

# Generics

## Key Idea

Generics let you write reusable, type-safe APIs without falling back to weakly typed code (such as `Any` plus `as!` casts). You write the code once with a type parameter (e.g. `T`), and each use site fills in a concrete type; the compiler checks types at compile time, so there are no runtime cast failures. A constraint like `T: Decodable` limits which types are allowed and tells the compiler which operations you may use on `T`.

## Example

```swift
struct APIResponse<T: Decodable>: Decodable {
    let data: T
}
```

## Practice Questions

- Why is the Equatable constraint necessary on an EquatableStack's contains(_:) method that a plain generic Stack<Element> cannot support?

## Senior Take

A good senior answer explains where generics improve API clarity and where generic-heavy design becomes hard to read and maintain.

## Practice Question Answers

### Why is the Equatable constraint necessary on an EquatableStack's contains(_:) method that a plain generic Stack<Element> cannot support?

Because `contains(_:)` has to compare elements with `==`, and for an unconstrained `Element` the compiler knows nothing about the type, so it does not allow calling `==`.

The mechanism: Swift type-checks generic code once, at the definition, not separately for each concrete type like C++ templates. Inside `Stack<Element>` the compiler only allows operations every possible `Element` supports — storing, returning, copying. `Element` could be a closure `() -> Void`, and closures cannot be compared. Writing `Element: Equatable` makes a promise the compiler checks at the use site: `EquatableStack<Int>` is valid, while `EquatableStack<() -> Void>` is a compile error.

Trade-off: a whole separate `EquatableStack` type duplicates code, and a stack of `Int` has to choose between two types. The idiomatic Swift approach is a conditional extension, the same way `Array` (via `Sequence`) only has `contains(_:)` when `Element: Equatable`. The example below assumes `Stack` stores its elements in `private var items: [Element]` and the extension is in the same file (so it can access `private`):

```swift
extension Stack where Element: Equatable {
    func contains(_ element: Element) -> Bool {
        items.contains(element)
    }
}
```

That way `Stack<Int>` gets `contains`, while `Stack<() -> Void>` still works, just without this method. If you need a different comparison rule, add a `contains(where:)` that takes a predicate.

## Interview Traps

### "Swift generics are like C++ templates, always specialized, so they cost nothing?"

**Common wrong answer:** Yes, the compiler generates a separate copy of the code for each concrete type, so generics are always as fast as hand-written code.

**Better answer:** Specialization is only an optimization, not a guarantee. Generic code can run unspecialized, passing type metadata and witness tables at runtime — common when calling across a module boundary where the function is not marked `@inlinable`, and in Debug builds (`-Onone`) there is almost no specialization. Within the same module with optimization on (Release), the compiler usually specializes. This is also why Swift type-checks generics at the definition: the code must be correct for every type that satisfies the constraints.

### "Can a Box<Cat> be used where a Box<Animal> is expected, if Cat subclasses Animal?"

**Common wrong answer:** Yes, because `[Cat]` can be passed where `[Animal]` is expected, so any generic type works the same way.

**Better answer:** No. User-defined generics in Swift are invariant: `Box<Cat>` and `Box<Animal>` are unrelated types. `Array`, `Optional`, `Dictionary` and `Set` get special compiler treatment for covariance (and some conversions, e.g. `[Cat]` to `[any P]`, must build a new array). For your own types you convert explicitly, e.g. `let animalBox = Box<Animal>(value: catBox.value)`.

### "Inside a generic function, does calling a function with an Int overload run the Int overload when T is Int?"

**Common wrong answer:** Yes, Swift picks the best matching overload based on the actual type at runtime.

**Better answer:** No. The overload is chosen at compile time based on what the compiler knows about `T` at the call site. In `func log<T>(_ x: T) { describe(x) }`, the compiler only knows `T` is "some type", so it always calls the generic `describe<T>(_:)`, even when you pass an `Int` and a `describe(_: Int)` exists. If behaviour must vary by type, use a protocol requirement (dispatched via the witness table), not overloads.

## Exercise

Implement a generic `Stack<Element>` with `push(_:)`, `pop() -> Element?`, and `peek() -> Element?`. Add a second version `EquatableStack<Element: Equatable>` that adds a `contains(_ element: Element) -> Bool` method. Write 3 usage examples showing why the generic constraint on the second version is necessary.
