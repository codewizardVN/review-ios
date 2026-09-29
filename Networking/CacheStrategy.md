[English](./CacheStrategy.md) | [Tiếng Việt](./CacheStrategy.vi.md)

[← Networking](./README.md)

# Cache Strategy

## Layers of Caching

1. **HTTP cache** — `URLCache`, managed by the URL Loading System; with the default cache policy (`.useProtocolCachePolicy`) it automatically honors the server's `Cache-Control` and `ETag`/`Last-Modified` headers, including sending revalidation requests when needed.
2. **In-memory cache** — `NSCache` for fast, size-limited access; the system may evict items at any time when memory is tight, so use it only for data you can reload.
3. **Disk cache** — your own files or a database; persists across launches. File caches should live in the `Caches` directory (excluded from backups, and the system may purge it when storage runs low).

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
| Image / asset caching | In-memory + disk (e.g. `NSCache` + files in the `Caches` directory) |
| Offline-first structured data | Database (CoreData, SwiftData, SQLite) |
| User-specific data | Do not cache at HTTP layer |

## Practice Questions

- Which layer should own caching?
- How do you avoid serving stale data after a logout?

## Senior Take

Caching decisions belong in the data layer, not the ViewModel. The domain should not know how data is stored or where it comes from.

## Practice Question Answers

### Which layer should own caching?

The data layer — usually the repository — should own caching decisions: when to read the cache, when to hit the network, how long entries live and when to clear them.

The reason: the repository is the one place that knows every data source (network, memory, disk) and returns domain models to the rest of the app. If a ViewModel checks "is there a cache, is it stale" itself, the caching logic is duplicated per screen and each screen ends up with its own definition of "stale". The domain and UI should just ask "give me the feed" and receive data, possibly with metadata like `lastUpdated` to display.

The cache layers underneath have their own roles but are still driven by the data layer:
- **HTTP cache (`URLCache`)** is controlled by the server through `Cache-Control`/`ETag`; the client only chooses the `cachePolicy` and configures capacity.
- **Memory/disk cache for images** is usually a separate component (like `ThumbnailCache`) used by the image loader, because images differ greatly from structured data in size and access frequency.
- **A database** for data that needs querying or offline use.

Trade-off: putting everything in the repository can bloat it; then extract a separate `CachePolicy` or `CacheStore` that the repository uses, but the decision still lives in the data layer rather than moving up to the ViewModel.

### How do you avoid serving stale data after a logout?

Treat every cache holding user data as belonging to that user's session, and clear (or throw away) all of it on logout — at every layer, not just one.

Logout checklist:
- Cancel in-flight requests, so a late response does not write the old user's data into a cache you just cleared.
- Call `URLCache.removeAllCachedResponses()` (or on your own session's cache) and clear cookies in `HTTPCookieStorage`.
- Call `removeAllObjects()` on every `NSCache`.
- Delete the user's database or data folder on disk, and the tokens in Keychain.
- Reset the state of singletons/repositories that hold data in memory.

A sturdier design scopes caches to the user from the start: create a "user session" object that owns its own `URLSession`, caches and repositories for that user; on logout you just `invalidateAndCancel()` the session and drop the whole object, instead of remembering to clear each place. You can also namespace keys or folders by user ID, so a different user logging in can never read the wrong data.

For sensitive data, consider not caching at the HTTP layer at all: use `URLSessionConfiguration.ephemeral`, or have the server send `Cache-Control: no-store`.

Trade-off: wiping everything makes the next login slower because data must be reloaded, but leaking data between two accounts is a far more serious bug.

## Interview Traps

### Does an `NSCache` with `countLimit = 50` guarantee it always keeps the 50 most recent items?

**Common wrong answer:** "Yes, it works like a 50-element LRU cache."

**Better answer:** `countLimit` and `totalCostLimit` are not exact limits; `NSCache` may evict items at any time (under memory pressure, or when the app goes to the background) and does not promise LRU order. So your code must always handle `image(for:)` returning `nil`. Its advantages over a `Dictionary`: `NSCache` is thread-safe, frees memory automatically when memory is tight, and does not copy its keys.

### You configured `URLCache`, so why is the response still not cached?

**Common wrong answer:** "`URLCache` caches every GET response."

**Better answer:** The URL Loading System only stores a response when it qualifies: HTTP/HTTPS, a status in the 2xx range, session and request cache policies that allow it, server headers that do not forbid caching (such as `no-store`), and a small enough size — with a disk cache, the response must be no larger than about 5% of the disk capacity. If the server does not send sensible `Cache-Control`/`ETag` headers, the client can hardly cache correctly. You can inspect and adjust this in the `urlSession(_:dataTask:willCacheResponse:completionHandler:)` delegate method.

### Is `.returnCacheDataElseLoad` a good way to do "cache-first"?

**Common wrong answer:** "Yes, use the cache if present, otherwise hit the network — classic offline-first."

**Better answer:** This policy returns cached data no matter how old it is and never revalidates with the server, so as long as a cached entry exists the user never sees fresh data. For structured data, keep `.useProtocolCachePolicy` so headers are honored, and implement cache-first yourself in the repository (read the database, display, then refresh). `.returnCacheDataDontLoad` only fits when you know for sure you are offline.

## Exercise

Implement a `ThumbnailCache` using `NSCache<NSString, UIImage>` with a 50-item count limit. Add `store(_:for:)` and `image(for:) -> UIImage?`. Write a comment explaining: (1) what happens to cached items under memory pressure, (2) why `NSCache` is preferable to a plain `Dictionary` for this use case, (3) what cache layer you would add if thumbnails need to persist across app launches.
