[English](./ErrorHandling.md) | [Tiếng Việt](./ErrorHandling.vi.md)

[← Swift Core](./README.md)

# Error Handling

## What To Review

- `throws`: marks a function that can fail; callers must call it with `try` (inside a `do-catch` or inside a function that also `throws`).
- `do-catch`: catches and handles errors; you can have several `catch` clauses with patterns (e.g. `catch NetworkError.unauthorized`), and a final `catch` with no pattern binds `error`. Also `try?` (error becomes `nil`) and `try!` (crashes on error).
- Typed domain errors: define your own error types (usually an `enum` conforming to `Error`) that describe the domain's real failure cases, instead of throwing `NSError` or strings. Do not confuse this with Swift 6's typed throws feature `throws(MyError)` (see below).
- Mapping low-level errors into user-meaningful errors: e.g. the network layer receives `URLError`/`DecodingError`, the data layer turns it into `NetworkError.timeout`, and only the UI layer decides to show "Connection lost, please try again".

## Example

```swift
enum NetworkError: Error {
    case invalidResponse
    case unauthorized
    case timeout
}
```

## Practice Questions

- How does a full do-catch that handles each ParseError case (missingField, invalidFormat, unsupportedVersion) with a distinct user-facing message differ from just using try?

## Senior Take

Avoid leaking raw infrastructure errors directly to the UI. Explain how errors are translated across layers.

## Practice Question Answers

### How does a full do-catch that handles each ParseError case (missingField, invalidFormat, unsupportedVersion) with a distinct user-facing message differ from just using try?

`try?` turns every error into `nil` and throws the error information away, while `do-catch` keeps the error so you can tell the cases apart and react differently to each one.

The mechanism: `try? parseConfig(from: data)` returns `Config?`. When the result is `nil`, you do not know which field is missing, where the format is wrong, or whether the version is unsupported — the UI can only show a generic sentence. With `do-catch` you pattern match each case, pull out its associated values (field name, version) to show a specific message, log it for the team, or choose a recovery path — for example, suggest updating the app on `unsupportedVersion`.

Swift 6 adds typed throws (SE-0413). If you declare the function as `func parseConfig(from data: Data) throws(ParseError) -> Config` and mark the block `do throws(ParseError)`, the compiler knows the exact error type, so `error` in the `catch` has type `ParseError` (not `any Error`) and a `switch` can be exhaustive without a `default` branch. Every `try` in that block must throw only `ParseError` (here `apply` is assumed not to throw):

```swift
do throws(ParseError) {
    let config = try parseConfig(from: data)
    apply(config)
} catch {
    switch error {
    case .missingField(let name): show("Missing field \(name)")
    case .invalidFormat(let field, let value): show("\(field) has an invalid format: \(value)")
    case .unsupportedVersion(let v): show("Version \(v) is not supported, please update the app")
    }
}
```

With plain `throws` you always need a general `catch` as well, because the function may throw any `Error`. `try?` is still reasonable when failure really just means "no value", such as reading a cache.

## Interview Traps

### "Swift 6 has typed throws, so should you use throws(MyError) everywhere?"

**Common wrong answer:** Yes, typed throws is always better because it is more type-safe, so replace every `throws` with `throws(SomeError)`.

**Better answer:** The SE-0413 proposal itself recommends untyped `throws` as the default. Typed throws fits code within one module or a small library where the set of errors is truly fixed, Embedded Swift, or generic functions that just forward a closure's error. In a public API it locks you into one error type: adding a case breaks callers' exhaustive `switch` statements, and lower-level errors (URLError, DecodingError) have to be wrapped by hand.

### "Where does an error thrown inside Task { } go?"

**Common wrong answer:** The app crashes, or the error shows up in the console / is reported to the caller automatically.

**Better answer:** An unstructured `Task { try await ... }` stores the error in its own result. If nobody does `await task.value` (or `task.result`), the error is silently swallowed — no crash, no log. So a `Task` body should have its own `do-catch` that updates UI state or logs, instead of letting the error escape.

### "Showing error.localizedDescription in the UI is good enough, right?"

**Common wrong answer:** Yes, every `Error` has a `localizedDescription`, so just display it.

**Better answer:** For a custom enum like `ParseError`, `localizedDescription` only returns a generic sentence like "The operation couldn't be completed. (App.ParseError error 0.)". To get a proper message, conform to `LocalizedError` and implement `errorDescription` (optionally `recoverySuggestion`). Even better, keep the split clear: the domain layer keeps structured errors, and the presentation layer decides the wording shown to the user.

## Exercise

Define a `ParseError` enum with cases: `missingField(String)`, `invalidFormat(String, String)`, and `unsupportedVersion(Int)`. Write a `parseConfig(from data: Data) throws -> Config` function that throws these errors. Write the call site with a full `do-catch` that handles each case with a distinct user-facing message. Explain how this differs from just using `try?`.
