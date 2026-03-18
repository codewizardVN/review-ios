[English](./Generics.md) | [Tiếng Việt](./Generics.vi.md)

[← Swift Core](./README.md)

# Generics

## Key Idea

Generics let you write reusable, type-safe APIs without falling back to weakly typed code.

## Example

```swift
struct APIResponse<T: Decodable>: Decodable {
    let data: T
}
```

## Senior Take

A good senior answer explains where generics improve API clarity and where generic-heavy design becomes hard to read and maintain.

## Exercise

Implement a generic `Stack<Element>` with `push(_:)`, `pop() -> Element?`, and `peek() -> Element?`. Add a second version `EquatableStack<Element: Equatable>` that adds a `contains(_ element: Element) -> Bool` method. Write 3 usage examples showing why the generic constraint on the second version is necessary.
