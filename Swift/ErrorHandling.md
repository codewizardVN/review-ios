[English](./ErrorHandling.md) | [Tiếng Việt](./ErrorHandling.vi.md)

[← Swift Core](./README.md)

# Error Handling

## What To Review

- `throws`
- `do-catch`
- Typed domain errors
- Mapping low-level errors into user-meaningful errors

## Example

```swift
enum NetworkError: Error {
    case invalidResponse
    case unauthorized
    case timeout
}
```

## Senior Take

Avoid leaking raw infrastructure errors directly to the UI. Explain how errors are translated across layers.

## Exercise

Define a `ParseError` enum with cases: `missingField(String)`, `invalidFormat(String, String)`, and `unsupportedVersion(Int)`. Write a `parseConfig(from data: Data) throws -> Config` function that throws these errors. Write the call site with a full `do-catch` that handles each case with a distinct user-facing message. Explain how this differs from just using `try?`.
