[English](./RequestResponseMapping.md) | [Tiếng Việt](./RequestResponseMapping.vi.md)

[← Data and Networking](./README.md)

# Request and Response Mapping

## Key Idea

Keep transport-layer types separate from domain-layer types. Requests and responses should reflect API contracts, while domain models should reflect app behavior.

## Why It Matters

- API fields often have naming or nullability that do not fit UI needs
- Domain models should be stable even if backend payloads change
- Mapping is the right place to normalize defaults and translate raw errors

## Example

```swift
struct UserDTO: Decodable {
    let id: String
    let fullName: String
    let avatarURL: URL?
}

struct User {
    let id: String
    let displayName: String
    let avatarURL: URL?
}

extension UserDTO {
    func toDomain() -> User {
        User(id: id, displayName: fullName, avatarURL: avatarURL)
    }
}
```

## Practice Questions

- When is it acceptable to skip DTOs?
- Where should mapping live: service, repository, or use case?

## Senior Take

Mapping is not busywork. It creates a boundary that protects the UI and domain from backend churn. Skip that boundary only when the app is small and the payload shape already matches product behavior.

## Exercise

Design a `FeedItemDTO` returned from the API with `created_at`, `author_name`, and optional `image_url`. Map it into a domain `FeedItem` used by the UI. Then explain where you would handle missing or invalid fields.
