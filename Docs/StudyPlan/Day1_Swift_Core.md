[English](./Day1_Swift_Core.md) | [Tiếng Việt](./Day1_Swift_Core.vi.md)

# Day 1: Swift Core

## Goal

Build a strong foundation in the Swift concepts that matter most for senior iOS interviews and real-world design decisions.

## Topics

- [x][Value Types and Reference Types](../../Swift/ValueTypes.md) — `struct` vs `class`, value semantics vs reference semantics
- [x][ARC and Memory Management](../../Swift/ARC.md) — ARC, retain cycles
- [][Protocol-Oriented Programming](../../Swift/Protocols.md)
- [][Generics](../../Swift/Generics.md)
- [][Error Handling](../../Swift/ErrorHandling.md)
- [][Access Control](../../Swift/AccessControl.md)
- [][Opaque Types](../../Swift/OpaqueTypes.md) — `any` vs `some`

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
