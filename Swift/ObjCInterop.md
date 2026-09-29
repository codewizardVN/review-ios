[English](./ObjCInterop.md) | [Tiếng Việt](./ObjCInterop.vi.md)

[← Swift Core](./README.md)

# Objective-C Interop

## Key Idea

Most senior roles touch a codebase that isn't pure Swift. Interop is about knowing exactly which Swift features survive the bridge to Objective-C, and why a runtime feature you rely on (dynamic dispatch, KVO, selectors) sometimes silently stops working.

## What To Review

- `@objc` and `@objcMembers` — expose a Swift declaration to the Objective-C runtime; required for selectors, KVO, and Interface Builder actions
- Bridging header — how a mixed-target project exposes Objective-C headers to Swift (`-Bridging-Header.h`) and Swift declarations to Objective-C (auto-generated `-Swift.h`)
- What can't bridge — Swift-only generics, enums with associated values, your own structs (unlike the pre-bridged types such as `String`, `Array`, `Dictionary`, `Date`, `URL`), and protocol extensions have no Objective-C representation
- `dynamic` — forces Objective-C message dispatch instead of Swift's static/vtable dispatch, required for method swizzling and some KVO paths
- `NSObject` subclassing — needed for APIs that expect Objective-C identity (`isEqual:`, `hash`, `NSCoding`, many delegate protocols predating Swift)
- Selector safety — `#selector(...)` is compile-time checked, but a selector built from a string, or a method never marked `@objc`, fails silently or crashes at runtime
- Nullability annotations (`_Nullable`, `_Nonnull`, `NS_ASSUME_NONNULL_BEGIN`) — how Objective-C headers become optionals vs implicitly-unwrapped optionals in Swift
- Incremental migration strategy — wrapping legacy Objective-C singletons behind a Swift protocol so new code never touches the old type directly

## Example

```objc
// Legacy.h
NS_ASSUME_NONNULL_BEGIN
@interface LegacySessionManager : NSObject
+ (instancetype)shared;
- (void)fetchTokenWithCompletion:(void (^)(NSString * _Nullable token, NSError * _Nullable error))completion;
@end
NS_ASSUME_NONNULL_END
```

```swift
// Swift call site — completion becomes (String?, Error?) -> Void.
// Because the completion follows the convention, the compiler also generates
// `func fetchToken() async throws -> String` so you can call it with `try await`.
LegacySessionManager.shared().fetchToken { token, error in
    guard let token else { return }
    self.session = token
}
```

## Practice Questions

- Does a `@objc private` method work when called via `perform(_:)`, and when does a `perform` call really crash with "unrecognized selector"?
- What happens if you forget `NS_ASSUME_NONNULL_BEGIN` in a legacy header a Swift module imports?
- Why can't a Swift `enum` with an associated value be exposed to Objective-C?

## Senior Take

Interop questions test whether you understand that Swift and Objective-C have two different dispatch and type models bolted together, not one language with two syntaxes. The strong answer names the actual boundary (what crosses, what doesn't, why) instead of "add `@objc` and it works." The other half of a senior answer is a migration plan: isolate legacy Objective-C behind a small Swift-facing protocol so the rest of the codebase never needs to reason about the bridge at all.

## Practice Question Answers

### Does a `@objc private` method work when called via `perform(_:)`, and when does a `perform` call really crash with "unrecognized selector"?

The direct answer: yes, it works fine. `private` by itself doesn't make it fail, because access control only exists at Swift compile time, and the Objective-C runtime knows nothing about it. A `@objc private func` is still registered with a selector; the target-action pattern `@objc private func didTap()` works fine every day.

When you really do hit an "unrecognized selector sent to instance" crash, the cause is usually one of these, and `private` is just a distracting detail:
- The method is missing `@objc` (for example someone removed `@objc` thinking `private` doesn't need it). Since Swift 4, `NSObject` subclasses no longer infer `@objc`, so the method is not in the runtime.
- A selector built from a string with the wrong name. `@objc private func load(id: String)` has the selector `loadWithId:`, not `"load"` or `"load:"`.
- Calling `perform` on the wrong object (for example an action's target was wired to an object that doesn't have that method).

```swift
perform(Selector("load"))              // crash: selector doesn't exist
perform(#selector(load(id:)), with: id) // compiler checks the name
```

The prevention is to always use `#selector(...)`, because the compiler checks that the method exists and is `@objc`. On the trade-off side: `perform(_:)` can only pass objects, not an `Int` or a struct safely, and it bypasses type checking. In new Swift code, a closure or protocol is almost always better.

### What happens if you forget `NS_ASSUME_NONNULL_BEGIN` in a legacy header a Swift module imports?

Every unannotated pointer is imported as an implicitly unwrapped optional (`String!`, `LegacySessionManager!`), meaning Swift doesn't know whether the value can be `nil`.

Mechanism: Objective-C allows any pointer to be `nil`. When the header says nothing, Swift can't guess, so it picks IUO as a compromise: the code compiles as if non-optional, but if the value really is `nil`, the app crashes right where it's used. With the header in the example, `+ (instancetype)shared` would become `LegacySessionManager!` instead of `LegacySessionManager`.

Practical consequences:
- The Swift API looks safe but isn't; `nil` errors show up at runtime instead of compile time.
- IUOs spread into the Swift code that calls it and are easily passed on elsewhere.
- If the header is only partially annotated, clang warns "pointer is missing a nullability type specifier".

The fix: wrap the header in `NS_ASSUME_NONNULL_BEGIN/END`, then mark `_Nullable` only where values really can be `nil`, like `token` and `error` in the completion. Trade-off: annotations must be true. Marking a value `nonnull` when it can actually be `nil` is more dangerous than leaving an IUO.

### Why can't a Swift `enum` with an associated value be exposed to Objective-C?

Because an Objective-C enum is just a C enum, a named integer, with no room to carry attached data.

Mechanism: `@objc enum` is only allowed with an integer raw type (`Int`, `UInt8`...), and it is imported as an `NS_ENUM`, essentially a constant. A Swift enum with associated values is a completely different kind of type: each case carries its own payload with its own type (`case success(User)`, `case failure(Error)`), and the memory layout is decided by Swift. Objective-C has no equivalent concept, so the compiler rejects `@objc` on such an enum.

Ways across the boundary:
- Split it into an `@objc enum` holding only the "kind" plus optional properties carrying the data.
- Wrap it in an `NSObject` class with a factory method per case.
- Use two callbacks or a `(value, error)` pair like the completion in the example.

```swift
@objc enum LoadStateKind: Int { case idle, loading, loaded, failed }
```

Trade-off: every approach loses the exhaustiveness and type safety of the Swift enum. Only build this shell at the interop boundary, and keep the original enum inside Swift.

## Interview Traps

### "Is adding `@objc` enough to swizzle a method or observe a property with KVO?"

**Common wrong answer:** "Yes, `@objc` means the method uses Objective-C message dispatch." `@objc` only exposes the method to the runtime; it doesn't change how Swift calls it.

**Better answer:** With `@objc` and no `dynamic`, Swift callers may still use vtable or static dispatch, or even inline it, so swizzling only affects Objective-C callers. KVO is the same: the property must be `@objc dynamic var` so the setter goes through `objc_msgSend` and KVO can inject its notifications. Without `dynamic`, `observe(\.x)` may silently never fire.

### "If a class inherits from `NSObject`, can every method be called from Objective-C?"

**Common wrong answer:** "Yes, `NSObject` subclasses expose everything automatically." That was only true before Swift 4.

**Better answer:** Since Swift 4 (SE-0160), the compiler no longer infers `@objc` for members of `NSObject` subclasses, except in cases like overriding an Objective-C method or implementing an `@objc` protocol. To expose a whole class, use `@objcMembers`, but that grows the binary and load time, so it's better to mark `@objc` on each member that needs it.

### "If the header is annotated `_Nonnull`, will Swift never receive `nil`?"

**Common wrong answer:** "Never, the compiler guarantees the annotation." An annotation is only a promise; it isn't checked at runtime.

**Better answer:** Clang can't stop an Objective-C implementation from returning `nil` for a value declared `nonnull`. Swift trusts the annotation and treats the value as non-optional, so when a `nil` really comes through the result depends on the type: it may crash, behave unpredictably, or be silently wrong (for example a nil `NSString` bridged into an empty `String`), usually at a spot that's hard to connect to the cause. For uncertain legacy code, it's safer to declare `_Nullable` and handle the optional in the Swift wrapper layer.

## Exercise

A legacy Objective-C `AnalyticsManager` singleton is used across 40 view controllers via direct static calls. Design a Swift protocol `AnalyticsTracking` that wraps it, explain which of its Objective-C methods can and cannot map cleanly to idiomatic Swift signatures (e.g., a method with a `NSDictionary *` payload of mixed types), and describe your rollout plan so both old and new call sites keep working during the migration.
