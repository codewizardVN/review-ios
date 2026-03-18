[English](./Codable.md) | [Tiếng Việt](./Codable.vi.md)

[← Networking](./README.md)

# Codable

## Key Idea

`Codable` (`Encodable + Decodable`) provides type-safe JSON serialization without manual parsing.

## What To Review

- `CodingKeys` — map JSON keys to Swift property names
- Custom `init(from:)` — handle complex or non-standard JSON structures
- `JSONDecoder` configuration — `keyDecodingStrategy`, `dateDecodingStrategy`
- DTOs vs domain models — decode into DTOs, then map to domain types

## Example

```swift
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

## Senior Take

Do not decode directly into domain models. Keep DTOs separate — the API contract and your domain model should be able to evolve independently. Mapping at the data layer boundary keeps the domain clean.

## Exercise

Given JSON `{"user_id":"u1","display_name":"Alice","joined_at":"2024-03-15T10:00:00Z"}`, write a `UserDTO` with `CodingKeys` mapping snake_case keys. Write a `User` domain model with different property names. Add a `toDomain() -> User` method. Configure `JSONDecoder` with `.iso8601` date strategy. Explain in a comment what breaks if the domain model decodes JSON directly.
