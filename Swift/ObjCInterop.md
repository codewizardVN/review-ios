[English](./ObjCInterop.md) | [Tiếng Việt](./ObjCInterop.vi.md)

[← Swift Core](./README.md)

# Objective-C Interop

## Key Idea

Most senior roles touch a codebase that isn't pure Swift. Interop is about knowing exactly which Swift features survive the bridge to Objective-C, and why a runtime feature you rely on (dynamic dispatch, KVO, selectors) sometimes silently stops working.

## What To Review

- `@objc` and `@objcMembers` — expose a Swift declaration to the Objective-C runtime; required for selectors, KVO, and Interface Builder actions
- Bridging header — how a mixed-target project exposes Objective-C headers to Swift (`-Bridging-Header.h`) and Swift declarations to Objective-C (auto-generated `-Swift.h`)
- What can't bridge — Swift-only generics, enums with associated values, structs, and protocol extensions have no Objective-C representation
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
// Swift call site — completion becomes (String?, Error?) -> Void
LegacySessionManager.shared().fetchToken { token, error in
    guard let token else { return }
    self.session = token
}
```

## Practice Questions

- Why would a `@objc` method marked `private` fail at runtime when called via `perform(_:)`?
- What happens if you forget `NS_ASSUME_NONNULL_BEGIN` in a legacy header a Swift module imports?
- Why can't a Swift `enum` with an associated value be exposed to Objective-C?

## Senior Take

Interop questions test whether you understand that Swift and Objective-C have two different dispatch and type models bolted together, not one language with two syntaxes. The strong answer names the actual boundary (what crosses, what doesn't, why) instead of "add `@objc` and it works." The other half of a senior answer is a migration plan: isolate legacy Objective-C behind a small Swift-facing protocol so the rest of the codebase never needs to reason about the bridge at all.

## Exercise

A legacy Objective-C `AnalyticsManager` singleton is used across 40 view controllers via direct static calls. Design a Swift protocol `AnalyticsTracking` that wraps it, explain which of its Objective-C methods can and cannot map cleanly to idiomatic Swift signatures (e.g., a method with a `NSDictionary *` payload of mixed types), and describe your rollout plan so both old and new call sites keep working during the migration.
