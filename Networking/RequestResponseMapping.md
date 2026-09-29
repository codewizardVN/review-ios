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

## Practice Question Answers

### When is it acceptable to skip DTOs?

You can skip DTOs when the payload genuinely matches how the app uses the data and the cost of changing it later is low.

Common cases:
- **Small apps, prototypes or experimental features**, where shipping speed matters more than long-term stability.
- **A backend your own team controls**, especially a BFF (backend-for-frontend) designed around the app's screens, so field names and nullability already fit the domain.
- **Simple, read-only data**, such as config or feature flags, with no business logic.
- **Types used only inside the data layer** that never reach the UI.

The condition for skipping safely: decoding still lives in a single place (the repository or API client), so on the day the backend changes you only insert a DTO there without touching ViewModels or Views. Conversely, do not skip DTOs when the API belongs to a third party, the payload has many optional or badly named fields, several endpoints return the same entity in different shapes, or the data needs validation before use — like a `FeedItemDTO` whose `image_url` may be missing or malformed.

Trade-off: DTOs cost extra code but buy independence between the API and the domain; skipping them saves effort up front but turns every backend change into a change that ripples across the app.

### Where should mapping live: service, repository, or use case?

Mapping usually belongs in the repository (the data layer), because that is exactly the boundary between "data coming from some source" and "the domain model the rest of the app uses".

A simple division of roles:
- **Service / API client** handles transport only: build the request, send it, check the status, decode into a DTO. It does not need to know the domain.
- **Repository** calls the service (and possibly a cache or database), then calls `toDomain()` to return a `FeedItem`. Because the repository may combine several sources, it is the only place that needs to know what shape each source returns.
- **Use case** works only with domain models and business rules. If a use case receives DTOs, the domain depends on the API again — exactly what we wanted to avoid.

There is also a second kind of mapping: from domain to display data (formatting dates for the locale, building a "by \(author)" string). That belongs to presentation — a ViewModel or a formatter — not the repository.

Trade-off: in a small app with no use-case layer, mapping in the service is still acceptable as long as DTOs never leave the data layer. Mapping in a use case only makes sense when one use case must combine several specific DTOs — rare, and usually a sign the repository is missing a method.

## Interview Traps

### Should `toDomain()` always return a value and never fail?

**Common wrong answer:** "Yes, mapping just copies fields; if something is missing, assign a default."

**Better answer:** Mapping is where you decide your policy for bad data, and the answer differs per field. For required fields (such as `id`, or a `created_at` that fails to parse), `toDomain()` should throw or return `nil`, and the repository uses `compactMap` to drop that item and log it rather than breaking the whole feed. For optional fields (such as `image_url`), map to `nil` and let the UI show a placeholder. Assigning arbitrary defaults (like `Date()` for a broken creation date) silently produces wrong data. One more detail: if the DTO declares `image_url` as `URL?`, then `null` or a missing key gives `nil`, but a string that cannot form a `URL` (for example an empty string `""`) makes decoding throw and breaks the whole item. If you want "malformed means no image", keep `String?` in the DTO and convert with `URL(string:)` in `toDomain()`.

### Should you format `created_at` into a "2 hours ago" string inside `toDomain()`?

**Common wrong answer:** "Yes, so the UI only has to display it."

**Better answer:** The domain should keep a `Date`, because the display string depends on locale, time zone and the current time — "2 hours ago" is wrong an hour later. Formatting is a presentation concern (a ViewModel, a `FormatStyle`, or `Text(date, style: .relative)`). If the domain only keeps a string, you lose the ability to sort, compare and test by time.

### Is it fine to let `URLError` and `DecodingError` flow straight up to the ViewModel?

**Common wrong answer:** "Sure, the ViewModel can `switch` on the error to show a message."

**Better answer:** Then the ViewModel depends on transport and decoding details, and every change to how you call the network means changing the UI. The data layer should translate raw errors into meaningful domain errors such as `.offline`, `.unauthorized`, `.notFound`, `.invalidData`, so the ViewModel only decides how to present them. Keep the original error in logs or an associated value for debugging.

## Exercise

Design a `FeedItemDTO` returned from the API with `created_at`, `author_name`, and optional `image_url`. Map it into a domain `FeedItem` used by the UI. Then explain where you would handle missing or invalid fields.
