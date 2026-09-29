[English](./CacheStrategy.md) | [Tiếng Việt](./CacheStrategy.vi.md)

[← Networking](./README.vi.md)

# Chiến lược Cache

## Các tầng cache

1. **HTTP cache** — `URLCache` do URL Loading System quản lý; với cache policy mặc định (`.useProtocolCachePolicy`) nó tự tôn trọng các header `Cache-Control`, `ETag`/`Last-Modified` của server, kể cả gửi request revalidate khi cần.
2. **In-memory cache** — `NSCache` truy cập nhanh, có giới hạn kích thước; hệ thống có thể xóa bớt item bất cứ lúc nào khi thiếu bộ nhớ, nên chỉ dùng cho dữ liệu tải lại được.
3. **Disk cache** — tự lưu file hoặc dùng database; tồn tại qua các lần launch. File cache nên nằm trong thư mục `Caches` (không đi vào backup, hệ thống có thể dọn khi thiếu dung lượng).

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
| Cache image / asset | In-memory + disk (ví dụ `NSCache` + file trong thư mục `Caches`) |
| Offline-first structured data | Database (CoreData, SwiftData, SQLite) |
| Data theo user | Không cache ở HTTP layer |

## Câu hỏi thực hành

- Tầng nào nên sở hữu caching?
- Làm sao tránh phục vụ stale data sau khi logout?

## Câu hỏi luyện tập

- Tầng nào nên sở hữu việc caching?
- Làm sao bạn tránh trả về dữ liệu cũ sau khi logout?

## Góc nhìn Senior

Quyết định cache thuộc về data layer, không phải ViewModel. Domain không nên biết data được lưu như thế nào hay đến từ đâu.

## Đáp án câu hỏi luyện tập

### Tầng nào nên sở hữu việc caching?

Tầng data — thường là repository — nên sở hữu quyết định cache: khi nào đọc cache, khi nào gọi mạng, cache sống bao lâu và khi nào xóa.

Lý do: repository là nơi biết mọi nguồn dữ liệu (network, memory, disk) và trả về domain model cho phần còn lại của app. Nếu ViewModel tự kiểm tra "có cache chưa, cache cũ chưa", logic cache bị lặp lại ở mỗi màn hình và mỗi màn hình có một định nghĩa "stale" khác nhau. Domain và UI chỉ nên hỏi "cho tôi danh sách feed" rồi nhận dữ liệu, có thể kèm metadata như `lastUpdated` để hiển thị.

Các tầng cache bên dưới có vai trò riêng nhưng vẫn do data layer điều khiển:
- **HTTP cache (`URLCache`)** do server điều khiển qua `Cache-Control`/`ETag`; client chỉ chọn `cachePolicy` và cấu hình dung lượng.
- **Memory/disk cache cho ảnh** thường là một component riêng (như `ThumbnailCache`) mà image loader dùng, vì ảnh có kích thước và tần suất truy cập khác hẳn dữ liệu có cấu trúc.
- **Database** cho dữ liệu cần query hoặc cần dùng offline.

Trade-off: gom hết vào repository có thể khiến nó phình to; khi đó tách ra một `CachePolicy` hoặc `CacheStore` riêng để repository dùng, nhưng quyết định vẫn nằm trong data layer, không đẩy lên ViewModel.

### Làm sao bạn tránh trả về dữ liệu cũ sau khi logout?

Coi mọi cache chứa dữ liệu của user là thuộc về session của user đó, và xóa (hoặc vứt bỏ) toàn bộ khi logout — ở mọi tầng, không chỉ một tầng.

Checklist khi logout:
- Cancel các request đang chạy, để response đến muộn không ghi dữ liệu của user cũ vào cache sau khi đã xóa.
- Gọi `URLCache.removeAllCachedResponses()` (hoặc trên cache của session riêng) và xóa cookie trong `HTTPCookieStorage`.
- Gọi `removeAllObjects()` trên các `NSCache`.
- Xóa database hoặc thư mục dữ liệu của user trên disk, và token trong Keychain.
- Reset state của các singleton/repository đang giữ dữ liệu trong memory.

Cách thiết kế bền hơn là gắn cache với user ngay từ đầu: tạo một object "user session" chứa `URLSession`, cache và repository riêng cho user đó; khi logout chỉ cần `invalidateAndCancel()` session và bỏ cả object, thay vì phải nhớ xóa từng chỗ. Có thể namespace key hoặc thư mục theo user ID, để user khác đăng nhập không bao giờ đọc nhầm dữ liệu.

Với dữ liệu nhạy cảm, cân nhắc không cache ở HTTP layer: dùng `URLSessionConfiguration.ephemeral`, hoặc để server gửi `Cache-Control: no-store`.

Trade-off: xóa sạch mọi thứ khiến lần đăng nhập sau chậm hơn vì phải tải lại, nhưng lộ dữ liệu giữa hai tài khoản là lỗi nghiêm trọng hơn nhiều.

## Bẫy phỏng vấn

### `NSCache` với `countLimit = 50` có đảm bảo luôn giữ đủ 50 item gần nhất không?

**Dễ trả lời sai:** "Có, nó hoạt động như một LRU cache 50 phần tử."

**Nên trả lời:** `countLimit` và `totalCostLimit` không phải giới hạn chính xác; `NSCache` có thể evict item bất kỳ lúc nào (khi memory pressure, hoặc khi app vào background) và không cam kết thứ tự LRU. Vì vậy code luôn phải xử lý trường hợp `image(for:)` trả về `nil`. Điểm cộng so với `Dictionary`: `NSCache` thread-safe, tự giải phóng khi thiếu bộ nhớ và không copy key.

### Đã cấu hình `URLCache` rồi, tại sao response vẫn không được cache?

**Dễ trả lời sai:** "`URLCache` cache mọi response của GET request."

**Nên trả lời:** URL Loading System chỉ lưu response khi đủ điều kiện: HTTP/HTTPS, status trong dải 2xx, cache policy của session và request cho phép, header của server không cấm cache (như `no-store`), và kích thước đủ nhỏ — với disk cache, response không được lớn hơn khoảng 5% dung lượng disk. Server không gửi `Cache-Control`/`ETag` hợp lý thì client khó cache đúng. Có thể kiểm tra và chỉnh qua delegate `urlSession(_:dataTask:willCacheResponse:completionHandler:)`.

### Dùng `.returnCacheDataElseLoad` để làm "cache-first" có ổn không?

**Dễ trả lời sai:** "Ổn, có cache thì dùng, không có thì gọi mạng — đúng kiểu offline-first."

**Nên trả lời:** Policy này trả về cache bất kể dữ liệu đã cũ bao lâu và không revalidate với server, nên chừng nào cache còn thì user không bao giờ thấy dữ liệu mới. Với dữ liệu có cấu trúc, nên để `.useProtocolCachePolicy` tôn trọng header, và tự làm cache-first ở repository (đọc database, hiển thị, rồi refresh). `.returnCacheDataDontLoad` chỉ hợp khi bạn biết chắc đang offline.

## Bài tập

Implement `ThumbnailCache` dùng `NSCache<NSString, UIImage>` với giới hạn 50 item. Thêm `store(_:for:)` và `image(for:) -> UIImage?`. Viết comment giải thích: (1) điều gì xảy ra với cached item dưới memory pressure, (2) tại sao `NSCache` tốt hơn `Dictionary` thông thường cho use case này, (3) tầng cache nào bạn thêm nếu thumbnail cần persist qua các lần launch.
