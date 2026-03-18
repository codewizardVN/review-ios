[English](./AccessControl.md) | [Tiếng Việt](./AccessControl.vi.md)

[← Swift Core](./README.md)

# Access Control

## What To Review

- `private` — visible within the enclosing declaration and its extensions in the same file
- `fileprivate` — visible within the same source file
- `internal` — visible within the module (default)
- `public` — visible outside the module, but not subclassable/overridable
- `open` — visible outside the module and subclassable/overridable

## Senior Take

Access control is about API boundaries and reducing misuse, not just hiding implementation details.

## Exercise

Design a `KeychainStore` struct that stores a `private var items: [String: String]`. Expose a `public func read(key: String) -> String?` and a `public mutating func write(key: String, value: String)`. Keep `private func encrypt(_ value: String) -> String` internal. Write a comment for each access level explaining the design decision. Explain what would break if `items` were public.
