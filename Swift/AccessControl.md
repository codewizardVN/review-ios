[English](./AccessControl.md) | [Tiếng Việt](./AccessControl.vi.md)

[← Swift Core](./README.md)

# Access Control

## What To Review

- `private` — visible within the enclosing declaration and its extensions in the same file
- `fileprivate` — visible within the same source file
- `internal` — visible within the module (the default when nothing is written). An app target is one module; each framework/Swift package target is its own module.
- `package` — (Swift 5.9, SE-0386) visible to every module in the same Swift package, but not to code outside the package. Useful when splitting a package into several modules without making internal APIs `public`.
- `public` — visible outside the module, but code in other modules cannot subclass the class or override the member
- `open` — visible outside the module and subclassable/overridable from other modules; only for classes and class members

## Practice Questions

- How would you design a KeychainStore struct with the right access levels for its stored items, its public read/write methods, and its private encrypt helper, and what would break if items were made public?

## Senior Take

Access control is about API boundaries and reducing misuse, not just hiding implementation details.

## Practice Question Answers

### How would you design a KeychainStore struct with the right access levels for its stored items, its public read/write methods, and its private encrypt helper, and what would break if items were made public?

I would make `items` `private`, `read(key:)` and `write(key:value:)` `public`, and `encrypt(_:)` `private`; if `items` were public, outside code could write straight into the dictionary, skip `encrypt`, and break the rule "every stored value is encrypted".

The mechanism: access control lets the compiler protect the type's invariants. With `items` `private`, the only way to write data is `write`, and `write` always calls `encrypt` — so the invariant always holds without checks anywhere else. `encrypt` is an implementation detail; keeping it `private` means you can change the algorithm at any time without affecting anyone.

If `items` were `public`, three things break: plaintext can be stored via `store.items["token"] = "abc"`; `read` may receive unencrypted data and decrypt it incorrectly; and callers become coupled to `[String: String]`, so you can never switch to the real Keychain (`SecItemAdd`/`SecItemCopyMatching`) without breaking the API.

Practical note: because it has `public` members, `KeychainStore` itself must be a `public struct`, and you need to write a `public init()` because the memberwise initializer is not automatically public. If outside code only needs to read, `public private(set) var` is the middle ground. If the code lives only inside the app (one module), `internal` is enough and `public` is unnecessary.

## Interview Traps

### "Marking data private keeps sensitive data secure, right?"

**Common wrong answer:** Yes, `private` stops anyone from reading `items`, so the token is safe.

**Better answer:** Access control is only a compile-time check, not a security mechanism. At runtime the data is still in memory and readable through a debugger, on a jailbroken device, or even with `Mirror(reflecting: store).children` — Mirror still sees `private` stored properties. Sensitive data belongs in the real Keychain (Security framework), and its time in memory should be kept short.

### "A public struct gets a public memberwise initializer too, doesn't it?"

**Common wrong answer:** Yes, if the struct is public, the synthesized init is usable from other modules.

**Better answer:** No. The synthesized memberwise initializer is at most `internal`, and it becomes `private` if any stored property is `private`. Likewise, members inside a `public` type default to `internal`. For another module to create instances, you have to write a `public init(...)` yourself.

### "private isn't visible from extensions, so you need fileprivate, right?"

**Common wrong answer:** Right, to let an extension access it you must change `private` to `fileprivate`.

**Better answer:** That was Swift 3 behaviour. Since Swift 4 (SE-0169), `private` members are visible in extensions of the same type in the same file. `fileprivate` is only needed when a different type in the same file must access the member. A related point: `@testable import` only exposes `internal` symbols to tests, not `private` or `fileprivate` ones.

## Exercise

Design a `KeychainStore` struct that stores a `private var items: [String: String]`. Expose a `public func read(key: String) -> String?` and a `public mutating func write(key: String, value: String)`. Keep `private func encrypt(_ value: String) -> String` as a private implementation detail of `KeychainStore` (`private`, not `internal`), so only `write` can call it. Write a comment for each access level explaining the design decision. Explain what would break if `items` were public.
