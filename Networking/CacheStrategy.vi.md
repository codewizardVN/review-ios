[English](./CacheStrategy.md) | [Tiếng Việt](./CacheStrategy.vi.md)

[← Networking](./README.vi.md)

# Chiến lược Cache

## Các tầng cache

1. **HTTP cache** — `URLCache` tự động tôn trọng `Cache-Control` header
2. **In-memory cache** — `NSCache` truy cập nhanh, giới hạn kích thước; bị xóa khi memory pressure
3. **Disk cache** — custom file-based hoặc database-backed; tồn tại qua các lần launch

## `URLCache`

```swift
let config = URLSessionConfiguration.default
config.urlCache = URLCache(memoryCapacity: 10_000_000, diskCapacity: 50_000_000)
let session = URLSession(configuration: config)
```

## Khi nào dùng mỗi tầng

| Tình huống | Giải pháp |
|---|---|
| API có Cache-Control đúng | `URLCache` (miễn phí) |
| Cache image / asset | In-memory + disk (e.g. `NSCache` + file) |
| Offline-first structured data | Database (CoreData, SwiftData, SQLite) |
| Data theo user | Không cache ở HTTP layer |

## Câu hỏi thực hành

- Tầng nào nên sở hữu caching?
- Làm sao tránh phục vụ stale data sau khi logout?

## Góc nhìn Senior

Quyết định cache thuộc về data layer, không phải ViewModel. Domain không nên biết data được lưu như thế nào hay đến từ đâu.

## Bài tập

Implement `ThumbnailCache` dùng `NSCache<NSString, UIImage>` với giới hạn 50 item. Thêm `store(_:for:)` và `image(for:) -> UIImage?`. Viết comment giải thích: (1) điều gì xảy ra với cached item dưới memory pressure, (2) tại sao `NSCache` tốt hơn `Dictionary` thông thường cho use case này, (3) tầng cache nào bạn thêm nếu thumbnail cần persist qua các lần launch.
