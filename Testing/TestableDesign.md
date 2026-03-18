[English](./TestableDesign.md) | [Tiếng Việt](./TestableDesign.vi.md)

[← Testing](./README.md)

# Testable Design

## Principles That Make Code Testable

1. **Inject dependencies** — never instantiate dependencies internally
2. **Depend on protocols, not concretions** — easy to swap for fakes
3. **Separate side effects** — pure logic in one place, I/O at the boundary
4. **Avoid singletons and global state** — makes tests order-dependent and fragile
5. **Small, focused units** — large classes are hard to test because they do too much

## Signs That Architecture Is Not Testable

- ViewModels that call `URLSession.shared` directly
- Logic buried in `viewDidLoad` or `body`
- Shared mutable global state
- Initializers that spin up real services

## Practice Questions

- Should everything be tested?
- How much UI testing is enough without becoming flaky?

## Senior Take

Testability is a proxy for good design. A senior mindset optimizes confidence per cost — not test count at all costs. Write tests where failure would be painful, not everywhere equally.

## Exercise

Take this untestable code: a `ProfileViewController` that calls `URLSession.shared.dataTask` directly in `viewDidLoad`. Refactor it to be testable by extracting a `ProfileService` protocol, injecting it via initializer, and writing one unit test that does not touch the network.
