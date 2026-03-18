[English](./CacheStrategy.md) | [Tiếng Việt](./CacheStrategy.vi.md)

[← Networking](./README.md)

# Cache Strategy

## Layers of Caching

1. **HTTP cache** — `URLCache` respects `Cache-Control` headers automatically
2. **In-memory cache** — `NSCache` for fast, size-limited access; evicted under memory pressure
3. **Disk cache** — custom file-based or database-backed; persists across launches

## `URLCache`

```swift
let config = URLSessionConfiguration.default
config.urlCache = URLCache(memoryCapacity: 10_000_000, diskCapacity: 50_000_000)
let session = URLSession(configuration: config)
```

## When Each Layer Applies

| Scenario | Solution |
|---|---|
| API has proper Cache-Control | `URLCache` (free) |
| Image / asset caching | In-memory + disk (e.g. `NSCache` + file) |
| Offline-first structured data | Database (CoreData, SwiftData, SQLite) |
| User-specific data | Do not cache at HTTP layer |

## Practice Questions

- Which layer should own caching?
- How do you avoid serving stale data after a logout?

## Senior Take

Caching decisions belong in the data layer, not the ViewModel. The domain should not know how data is stored or where it comes from.

## Exercise

Implement a `ThumbnailCache` using `NSCache<NSString, UIImage>` with a 50-item count limit. Add `store(_:for:)` and `image(for:) -> UIImage?`. Write a comment explaining: (1) what happens to cached items under memory pressure, (2) why `NSCache` is preferable to a plain `Dictionary` for this use case, (3) what cache layer you would add if thumbnails need to persist across app launches.
