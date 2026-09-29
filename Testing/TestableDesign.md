[English](./TestableDesign.md) | [Tiếng Việt](./TestableDesign.vi.md)

[← Testing](./README.md)

# Testable Design

## Principles That Make Code Testable

1. **Inject dependencies** — do not create dependencies with side effects (network, database, clock, analytics) inside the class; receive them through the initializer so tests can pass in fakes. A default value for production is fine, for example `init(service: ProfileService = LiveProfileService())`, as long as tests can still replace it.
2. **Depend on protocols (or closures) at the boundary, not concretions** — for slow or external dependencies, the code only knows the protocol, so tests can easily swap in a fake. Pure logic does not need a protocol (see the interview trap below).
3. **Separate side effects** — pure logic (calculations, decisions) in one place, I/O (API calls, file writes, reading the clock) at the boundary. Pure logic can be tested with just inputs and outputs, no fakes needed.
4. **Avoid singletons and global state** — shared state lets one test affect another, so results depend on execution order and break easily when tests run in parallel.
5. **Small, focused units** — a large class does too much, so testing one part means building the whole thing; split it and each part can be tested on its own.

## Signs That Architecture Is Not Testable

- ViewModels that call `URLSession.shared` directly: tests cannot replace the real network with fake data.
- Logic buried in `viewDidLoad` or `body`: you must build a view hierarchy just to run the logic.
- Shared mutable global state: tests overwrite each other's state.
- Initializers that spin up real services (open connections, read the database, start timers): merely creating the object for a test triggers side effects.

## Practice Questions

- Should everything be tested?
- How much UI testing is enough without becoming flaky?

## Senior Take

Testability is a proxy for good design. A senior mindset optimizes confidence per cost — not test count at all costs. Write tests where failure would be painful, not everywhere equally.

## Practice Question Answers

### Should everything be tested?

No. You should *design* so that everything important can be tested, but only *write* tests where a failure has real consequences or the logic is complex enough to get wrong.

These two ideas often get merged into one. Testability is a property of the design: dependencies are injected, logic is separate from I/O, there is no global state. With that in place, writing a test when you need one is cheap. Whether to actually write a test is an investment decision:

- **Worth testing**: business rules, money calculations, state machines, parsing, error handling, code shared across many places, and bugs that already happened.
- **Can skip**: pure wiring code (calls straight into a dependency), simple view layout, prototypes about to be thrown away, and Apple framework behaviour.

A useful framing is "confidence per cost": every test costs time to write, time to run and maintenance every time the code changes. Low-level (unit) tests are cheap and fast, so cover most logic there; high-level (UI) tests are expensive, so keep them for a few key journeys.

Trade-off: when a team makes "test everything" a rule, it usually produces tests that mirror the implementation, break on refactors, and make people afraid to change code. The purpose of tests is to make changing code safer, not slower.

### How much UI testing is enough without becoming flaky?

Enough means each of the business's most important journeys has one UI test for its happy path, while every other variation is pushed down to unit tests; for most apps that is a few dozen tests, not hundreds.

The reason is that UI tests run through the real app, the simulator, animations and the accessibility tree, so each extra test adds another source of non-determinism. The more tests you have, the higher the chance that at least one fails randomly on every CI run, and the team starts hitting "re-run" instead of reading failures.

Signs you have too many UI tests:

- They check validation, text formatting or error branches that unit tests could cover.
- The suite takes so long that developers do not run it before merging.
- The flaky rate goes above roughly 1–2% and nobody fixes it.

To keep the suite small yet trustworthy: use stubbed data via launch arguments, stable `accessibilityIdentifier`s, condition-based waits instead of `sleep`, and track the flaky rate of each test. Fix a consistently flaky test right away, or quarantine it and rewrite it; do not let it erode trust in the whole suite.

## Interview Traps

### "To make code testable, every class should come with a protocol, right?"

**Common wrong answer:** Yes, every service, ViewModel and helper needs a protocol so it can be replaced by a fake.

**Better answer:** Protocols are only needed at the *boundary* with things that are slow, non-deterministic or external: network, database, clock, analytics. Pure logic (formatters, validators, reducers) should be tested directly with the real implementation, no protocol needed. Creating a 1:1 protocol for every class adds files and indirection without adding confidence. Besides protocols, a dependency can also be a closure, for example `init(fetch: @escaping () async throws -> Profile)`, which is leaner for a dependency with a single behaviour.

### "A private method contains important logic. How do you test it?"

**Common wrong answer:** Change `private` to `internal` and use `@testable import` to call it directly.

**Better answer:** Test the private method *through* the public API that calls it, because that is the behaviour the class's users actually see. `@testable import` only opens up `internal` access, not `private`. If the private logic is complex enough that you want to test it on its own, that is a sign it should be extracted into its own type (for example `PriceCalculator`) with its own API; testing that type directly is then appropriate.

### "This function uses `Date()` to check whether a token has expired. It is still testable, you just run it, right?"

**Common wrong answer:** Yes, `Date()` is a standard API so there is no need to inject it.

**Better answer:** `Date()` is a hidden dependency on the system clock, so tests for "already expired" or "about to expire" cannot run reliably. Inject time instead, for example `init(now: @escaping () -> Date = Date.init)`, so the test can pass in a fixed date. Similarly, code that uses `Task.sleep` or debouncing can accept an `any Clock<Duration>` (iOS 16+) so tests can substitute a controllable clock. Apple does not ship a test clock; write your own or use a library such as Point-Free's swift-clocks (`TestClock`, `ImmediateClock`). `UUID()` and randomness should be injected the same way.

## Exercise

Take this untestable code: a `ProfileViewController` that calls `URLSession.shared.dataTask` directly in `viewDidLoad`. Refactor it to be testable by extracting a `ProfileService` protocol, injecting it via initializer, and writing one unit test that does not touch the network.
