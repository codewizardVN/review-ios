[English](./OpaqueTypes.md) | [Tiếng Việt](./OpaqueTypes.vi.md)

[← Swift Core](./README.md)

# Opaque Types: `any` vs `some`

## Key Idea

- `some Protocol` (opaque type, available in return position since Swift 5.1) — the concrete type is hidden but fixed at compile time. In return position the function itself (the callee) picks the type and hides its name from the caller, which is why it is called "reverse generics". The compiler still knows the real type, so no existential "box" is needed.
- `any Protocol` (existential; the `any` keyword arrived in Swift 5.6) — a "box" that can hold any conforming type, and the type inside can vary at runtime (e.g. an array holding several different types). The cost is dynamic dispatch through the witness table and possible heap allocation. Note: the Swift 6 language mode still does not require writing `any` (you can enforce it with the upcoming feature `ExistentialAny`), but writing it makes the existential explicit to readers.

## Example

```swift
// some: caller does not know the concrete type, but it is fixed
func makeView() -> some View { ... }

// any: can hold any conforming type — more flexible, less performant
var repo: any UserRepository
```

## Practice Questions

- Why does some Shape work for a factory function like makeDefaultShape() but any Shape become necessary for a function like largestShape(from shapes: [any Shape])?

## Senior Take

You should understand this well enough to discuss API design, performance trade-offs, and when existential types are the better fit.

## Practice Question Answers

### Why does some Shape work for a factory function like makeDefaultShape() but any Shape become necessary for a function like largestShape(from shapes: [any Shape])?

Because `makeDefaultShape()` always returns exactly one concrete type (`Circle`), while `largestShape` has to work with an array mixing `Circle` and `Rectangle`, and which type it returns is only known at runtime.

The mechanism: `some Shape` in return position means "one single concrete type whose name the caller does not need to know". The compiler still knows it is `Circle`, so there is no existential boxing and the compiler can optimize (static dispatch, specialization) as with a concrete type, and you can later switch to another type without breaking callers. But every return path must produce the same type — `if big { Circle() } else { Rectangle() }` is a compile error.

`any Shape` is an existential: a "box" holding the value (inline if small, on the heap if large) plus type metadata and a witness table, so each array element can be a different type. Writing `[some Shape]` as a parameter is equivalent to a generic `<S: Shape>` with `[S]` — every element must be the same type. The result of `largestShape` also depends on the data, so it can only be `any Shape`.

Trade-off: `any` adds cost (the box, dynamic dispatch, possible heap allocation) and loses type information. If the array is always homogeneous, a generic `func largest<S: Shape>(from shapes: [S]) -> S` is faster and keeps the concrete type for the caller.

## Interview Traps

### "What's the difference between some View and any View — aren't they just two spellings?"

**Common wrong answer:** Just different syntax; `body` can return `Text` in one branch and `Image` in another, so `some` is as flexible as `any`.

**Better answer:** `some View` is one type fixed at compile time; the compiler knows exactly what it is. `body` can return different views in an `if/else` because `@ViewBuilder` (the `body` requirement in the `View` protocol is marked `@ViewBuilder`, so your `body` gets it automatically) wraps them into a single type `_ConditionalContent<Text, Image>`, not because of `some`. A plain function returning `some View` without `@ViewBuilder` and with two branches of different types fails to compile. Using `AnyView` (type erasure) makes SwiftUI lose the type information it uses to diff efficiently.

### "What does some mean in parameter position?"

**Common wrong answer:** The same as in return position: the callee picks the type and hides it; or that it behaves like `any`.

**Better answer:** Since Swift 5.7 (SE-0341), `func draw(_ s: some Shape)` is just shorthand for `func draw<S: Shape>(_ s: S)`. In a parameter, the caller picks the type, and it is a statically dispatched generic, not an existential. So `some` in return position is "reverse generics" (the callee chooses), while in a parameter it is an ordinary generic (the caller chooses).

### "Does any Shape conform to Shape?"

**Common wrong answer:** Yes, so `[any Shape]` can be passed to any generic `<S: Shape>(_: [S])` function, and `any Equatable` values can be compared with `==`.

**Better answer:** In general an existential does not conform to its own protocol (exceptions: `any Error` conforms to `Error`, and some `@objc` protocols). Since Swift 5.7 (SE-0352), a single `any Shape` value is implicitly "opened" when passed to a `some Shape` or `<S: Shape>(_: S)` parameter, so the simple case works. But `[any Shape]` cannot be passed as `[S]`, and two `any Equatable` values cannot be compared with `==` because they may be of different types.

## Exercise

Write a protocol `Shape` with a `var area: Double` property. Create two conforming types: `Circle` and `Rectangle`. Write a function `makeDefaultShape() -> some Shape` that returns a `Circle`. Then write a function `largestShape(from shapes: [any Shape]) -> any Shape`. Explain in comments why `some` works for the factory function but `any` is needed for the array parameter.
