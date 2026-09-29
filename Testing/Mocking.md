[English](./Mocking.md) | [Tiếng Việt](./Mocking.vi.md)

[← Testing](./README.md)

# Mocking and Test Doubles

## Types of Test Doubles

| Type | Description |
| --- | --- |
| **Stub** | Returns a fixed value; does not verify calls |
| **Mock** | Verifies that specific calls were made |
| **Fake** | Lightweight working implementation (e.g. in-memory repository) |
| **Spy** | Records calls for later assertion |

## Preferred Approach in Swift

Use protocol-based fakes. Define a protocol, implement the real version in production, and implement a `Fake` version in tests.

```swift
protocol FeedRepository {
    func fetchFeed() async throws -> [FeedItem]
}

// Test fake
final class FakeFeedRepository: FeedRepository {
    var stubbedItems: [FeedItem] = []
    var fetchCallCount = 0

    func fetchFeed() async throws -> [FeedItem] {
        fetchCallCount += 1
        return stubbedItems
    }
}
```

## Practice Questions

- How do mocks differ from stubs?
- Should you use a mocking framework or write fakes manually?

## Senior Take

Manual fakes are usually clearer and safer than generated mocks. Mocking frameworks can obscure what is actually being tested. Reserve them for cases where the fake would be prohibitively complex to write by hand.

## Practice Question Answers

### How do mocks differ from stubs?

A stub only *supplies data* to the code under test, while a mock *checks interactions*: it verifies that the code called the right method, the right number of times, with the right arguments.

Think in terms of data direction:

- A **stub** handles indirect input. For example `stubbedItems` in `FakeFeedRepository` decides what `fetchFeed()` returns. The test then asserts on the SUT's *output*, like `sut.items.count == 1`. A stub never makes a test fail.
- A **mock** handles indirect output, meaning things the SUT "sends out" without returning: sending analytics, writing logs, calling a delete API. The assertion lives on the test double itself, for example "`trackPurchase` was called exactly once".

In Swift the lines often blur: `FakeFeedRepository` is both a stub (through `stubbedItems`) and a spy (through `fetchCallCount`, which records calls for a later assertion). What matters is knowing whether the test checks *state* or *interaction*.

When not to use a mock: when the result can be checked through state. Verifying interactions in too much detail (call order, secondary arguments) couples the test to the implementation, so a small refactor breaks it even though behaviour is still correct. Verify interactions only when the call itself is the behaviour you must guarantee, such as sending a payment event or not calling an API twice.

### Should you use a mocking framework or write fakes manually?

By default write protocol-based fakes by hand; use a framework or code generation only when the number of protocols grows so large that writing them by hand becomes a burden.

Why hand-written fakes suit Swift:

- Swift has no runtime mocking like Mockito in Java: structs, `final` classes and non-`dynamic` methods are dispatched statically or through a vtable fixed at compile time, pure Swift does not let you replace a method's implementation at runtime (no swizzling), and `Mirror` can only read values, not change behaviour. Swift tools (Mockolo, Sourcery, Cuckoo, or macros like Spyable) all *generate code* at build time, so you still need protocols.
- Hand-written fakes are easy to read: a reviewer sees immediately what `fetchFeed()` returns without learning a framework DSL.
- Fakes are reusable across many tests and can have real behaviour, for example an in-memory repository that stores and reads data.
- The compiler checks everything; change the protocol and the fake reports an error immediately.

When a framework is worth it: a codebase with hundreds of protocols with many methods, where fakes are mostly call-counting boilerplate. Code generation saves time, at the cost of an extra build step, an extra dependency, and tests that tend to verify interactions more than necessary. A senior should decide based on scale and document the convention for the team.

## Interview Traps

### "`FakeFeedRepository` in the example is a fake, right?"

**Common wrong answer:** Yes, because its name contains "Fake" and it implements the protocol.

**Better answer:** The name does not decide the kind of test double. By the strict definition this class is a stub (returns fixed `stubbedItems`) combined with a spy (counts `fetchCallCount`), not a fake, because it has no real behaviour. A true fake has working logic, for example storing items in a dictionary on `save()` and returning them on `fetch()`. In practice many teams call all of these "fakes", but in an interview you should be able to tell them apart to show you understand whether a test checks state or interaction.

### "Can you mock `URLSession` or any `final class` with a framework like Mockito?"

**Common wrong answer:** Yes, a mocking library can replace the methods of any class at runtime.

**Better answer:** Not in pure Swift. Calls to a `final class` or a struct are statically dispatched; methods of a non-`final` class go through a vtable, but that vtable is fixed at compile time, so the only way to change behaviour is to write a subclass that overrides them yourself, not to inject a mock at runtime as Mockito does. OCMock relies on the Objective-C runtime, so it only works with Objective-C/`NSObject` classes and methods called through message dispatch (`@objc dynamic`); it is not a general solution for Swift code. (`URLSession` is a non-`final` Objective-C class, but subclassing it to mock it is discouraged by Apple, and `URLSession.init()` has been deprecated since iOS 13.) The right approach is to put a protocol at the boundary (for example `FeedRepository`) and swap the implementation; for `URLSession` specifically you can use a custom `URLProtocol` in `URLSessionConfiguration.protocolClasses` to intercept requests without mocking the class.

### "Swift 6 complains when `FakeFeedRepository` conforms to a protocol that requires `Sendable`. Adding `@unchecked Sendable` fixes it?"

**Common wrong answer:** Yes, it is only test code, so turning off the check is fine.

**Better answer:** `@unchecked Sendable` only silences the diagnostic; it does not make the class safe. If tests (especially Swift Testing running in parallel) call the fake from several threads, `fetchCallCount += 1` is a real data race and produces random wrong results. Safer options are protecting state with `Mutex` from the Synchronization module (requires iOS 18+ / macOS 15+ and a Swift 6 toolchain): stored in a `let` of a `final class`, it lets the class conform to `Sendable` for real without `@unchecked`. If you must support older iOS versions, use `OSAllocatedUnfairLock` (iOS 16+) or `NSLock` (with `NSLock` you still need `@unchecked Sendable`, but now you really have protected the state). Another option is turning the fake into an `actor` when the protocol's methods are already `async`. If the SUT always runs on the main actor, you can also mark the fake `@MainActor`.

## Exercise

Create a `FakeAnalyticsService` that records every event name passed to it. Inject it into a `CheckoutViewModel` and assert that `trackPurchase()` is called exactly once after a successful order. Then explain: is this a mock, a stub, or a spy?
