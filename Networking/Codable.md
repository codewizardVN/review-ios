[English](./Codable.md) | [Tiếng Việt](./Codable.vi.md)

[← Networking](./README.md)

# Codable

## Key Idea

`Codable` (`Encodable + Decodable`) provides type-safe JSON serialization without manual parsing.

## What To Review

- `CodingKeys` — a `String, CodingKey` enum that declares the JSON key for each property (for example `displayName = "display_name"`); a property missing from `CodingKeys` is not decoded/encoded at all (so it must have a default value).
- Custom `init(from:)` — write the decoding yourself when the JSON is complex or non-standard: nested objects you want to flatten, a field that may be a number or a string, a default when a key is missing (`decodeIfPresent(...) ?? default`).
- `JSONDecoder` configuration — `keyDecodingStrategy` (for example `.convertFromSnakeCase` turns `display_name` into `displayName` automatically), `dateDecodingStrategy` (the default is `.deferredToDate`, i.e. seconds since 2001-01-01, so for ISO 8601 date strings you must set `.iso8601` or `.custom`).
- DTOs vs domain models — decode into a DTO (matching the JSON shape exactly), then map to a domain type (matching how the app uses the data).

## Example

```swift
// The decoder needs: decoder.dateDecodingStrategy = .iso8601 to read "created_at" as an ISO 8601 string
struct UserDTO: Decodable {
    let id: String
    let displayName: String
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case displayName = "display_name"
        case createdAt = "created_at"
    }
}
```

## Practice Questions

- What breaks if a domain User model decodes JSON directly instead of going through a UserDTO with CodingKeys mapping and a toDomain() conversion?

## Senior Take

Do not decode directly into domain models. Keep DTOs separate — the API contract and your domain model should be able to evolve independently. Mapping at the data layer boundary keeps the domain clean.

## Practice Question Answers

### What breaks if a domain User model decodes JSON directly instead of going through a UserDTO with CodingKeys mapping and a toDomain() conversion?

The domain `User` model becomes tightly bound to the API contract: whenever the backend renames a key, changes a date format or changes nullability, the decoding failure flows straight into the domain and every screen that uses `User`.

Concretely, what breaks:
- **Property names are dictated by the API.** `User` has to carry `CodingKeys` like `"user_id"` and `"joined_at"`; naming things in your domain's own language means touching decoding.
- **Nullability leaks into the domain.** If the API may return `display_name` as null, `User` needs a `String?`, and every call site has to unwrap it, even though in business terms a user always has a display name (possibly with a fallback).
- **There is no place to validate and normalize.** `toDomain()` is the natural place to trim strings, apply defaults, turn a `String` into a `URL`, or drop invalid data. Decoding directly gives you only two outcomes: success or throw.
- **Another endpoint returning a different shape** (say `/me` with extra fields) forces the domain model to accommodate both.
- **Tests and persistence get dragged along**: mock JSON and cached data must match the exact wire format.

Trade-off: a DTO adds one type and one mapping function per entity. For a small app where the team controls the payload and it matches the domain exactly, decoding directly is still acceptable — but splitting them later always costs more than doing it from the start.

## Interview Traps

### What happens if you use `keyDecodingStrategy = .convertFromSnakeCase` together with `CodingKeys` whose raw value is `"display_name"`?

**Common wrong answer:** "Nothing, the strategy is just a fallback and `CodingKeys` take priority."

**Better answer:** `JSONDecoder` first converts the JSON keys to camelCase (`display_name` becomes `displayName`) and only then compares them with the `CodingKeys` raw values. Since the raw value is still `"display_name"`, nothing matches and decoding throws `keyNotFound`. Pick one: use the strategy and keep `CodingKeys` in camelCase, or drop the strategy and map by hand. A small extra trap: `user_id` converts to `userId`, not `userID`.

### Can `dateDecodingStrategy = .iso8601` decode every ISO 8601 string?

**Common wrong answer:** "Yes, if the backend sends ISO 8601, `.iso8601` is enough."

**Better answer:** `.iso8601` does not accept fractional seconds, so `"2024-03-15T10:00:00.123Z"` fails and breaks the whole payload. If the backend may send fractional seconds, use `.custom` with `Date.ISO8601FormatStyle(includingFractionalSeconds: true)` and try both formats. Best of all, agree on the format with the backend and write decoding tests with real strings taken from the API.

### Does a property `var isVerified: Bool = false` use its default value when the key is missing from the JSON?

**Common wrong answer:** "Yes, Swift uses the default value if the key is not there."

**Better answer:** With compiler-synthesized `Decodable`, the default value of a `var` is ignored: it still calls `decode(Bool.self, forKey:)`, so a missing key throws `keyNotFound`. Only `Optional` properties are decoded with `decodeIfPresent` (a missing key or `null` both give `nil`). If you want a real default, write `init(from:)` with `decodeIfPresent(...) ?? false`, or make the DTO property Optional and apply the default in `toDomain()`. The same mechanism is why one bad element makes an entire `[UserDTO]` array fail to decode.

## Exercise

Given JSON `{"user_id":"u1","display_name":"Alice","joined_at":"2024-03-15T10:00:00Z"}`, write a `UserDTO` with `CodingKeys` mapping snake_case keys. Write a `User` domain model with different property names. Add a `toDomain() -> User` method. Configure `JSONDecoder` with `.iso8601` date strategy. Explain in a comment what breaks if the domain model decodes JSON directly.
