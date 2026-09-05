[English](./OpaqueTypes.md) | [Tiếng Việt](./OpaqueTypes.vi.md)

[← Swift Core](./README.md)

# Opaque Types: `any` vs `some`

## Key Idea

- `some Protocol` — the concrete type is hidden but fixed at compile time (reverse generics)
- `any Protocol` — existential storage that can hold any conforming type at runtime

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

## Exercise

Write a protocol `Shape` with a `var area: Double` property. Create two conforming types: `Circle` and `Rectangle`. Write a function `makeDefaultShape() -> some Shape` that returns a `Circle`. Then write a function `largestShape(from shapes: [any Shape]) -> any Shape`. Explain in comments why `some` works for the factory function but `any` is needed for the array parameter.
