[English](./OfflineFirst.md) | [Tiếng Việt](./OfflineFirst.vi.md)

[← Networking](./README.vi.md)

# Offline-First Design

## Ý chính

Hiển thị cached data ngay lập tức, fetch update trong background và xử lý trường hợp không có mạng một cách nhẹ nhàng thay vì block UI.

## Pattern

```text
1. Load từ cache → hiển thị ngay
2. Fetch từ network trong background
3. Cập nhật UI khi có data mới
4. Xử lý network failure ngầm (hoặc với non-blocking banner)
```

## Nội dung ôn tập

- `NWPathMonitor` (Network framework) — theo dõi trạng thái đường mạng (`.satisfied`, `.unsatisfied`, loại kết nối, có đắt/bị giới hạn không); dùng làm tín hiệu để kích hoạt sync hoặc cập nhật UI, không phải để chặn request (xem bẫy bên dưới).
- Optimistic UI — áp dụng thay đổi vào dữ liệu local và hiển thị ngay trước khi server xác nhận; nếu server từ chối thì phải rollback và báo cho user.
- Sync queue (outbox) — lưu các thao tác ghi vào một hàng đợi persist trên disk khi offline, rồi gửi lần lượt khi có mạng trở lại.
- Conflict resolution — khi cả client và server cùng sửa một bản ghi: last-write-wins (bản sửa sau cùng thắng), server-wins (bản trên server luôn thắng), hoặc merge (gộp theo từng field hoặc hỏi user).

## Câu hỏi thực hành

- Nếu API chậm hoặc không ổn định, bạn sẽ thiết kế data flow như thế nào?

## Câu hỏi luyện tập

- Nếu API chậm hoặc không ổn định, bạn sẽ thiết kế luồng dữ liệu như thế nào?

## Góc nhìn Senior

Offline-first là quyết định UX trước khi là quyết định kỹ thuật. Định nghĩa "offline" có nghĩa gì với từng tính năng: chỉ đọc cache? Cho phép write? Hiển thị staleness indicator? Căn chỉnh với product trước khi xây dựng sync layer.

## Đáp án câu hỏi luyện tập

### Nếu API chậm hoặc không ổn định, bạn sẽ thiết kế luồng dữ liệu như thế nào?

Tôi sẽ để database local làm nguồn sự thật duy nhất (single source of truth) cho UI, còn network chỉ là thứ cập nhật database ở background — UI không bao giờ phải chờ API mới hiển thị được.

Luồng đọc:
1. Màn hình observe dữ liệu từ database (`@Query`, `NSFetchedResultsController`, hoặc một `AsyncStream` do repository cung cấp) và hiển thị ngay những gì đang có.
2. Repository kích hoạt refresh: gọi API với timeout hợp lý, retry có backoff cho lỗi transient.
3. Khi có dữ liệu mới, repository ghi vào database; UI tự cập nhật vì đang observe, không cần callback riêng.
4. Nếu refresh thất bại, dữ liệu cũ vẫn hiển thị, kèm banner non-blocking "Cập nhật lần cuối X" dựa trên `lastUpdated`.

Luồng ghi:
- Áp dụng thay đổi vào database trước (optimistic UI) và, trong cùng transaction, ghi một bản ghi vào outbox (sync queue) được persist trên disk.
- Một sync worker gửi outbox khi có mạng, kèm idempotency key để retry an toàn, rồi đánh dấu hoàn tất, hoặc rollback và báo lỗi nếu server từ chối.
- Có chính sách conflict rõ ràng: server-wins, dùng version/`ETag` để phát hiện xung đột, hoặc merge theo từng field.

Trade-off: thiết kế này phức tạp hơn nhiều so với "gọi API rồi hiển thị" — cần schema local, migration, sync và xử lý conflict. Không phải tính năng nào cũng cần: màn hình thanh toán hay số dư tài khoản phải hiển thị dữ liệu mới nhất, nên ở đó chờ và báo lỗi rõ ràng tốt hơn là hiện dữ liệu cũ.

## Bẫy phỏng vấn

### Có nên kiểm tra `NWPathMonitor` trước khi gửi request, "không có mạng" thì khỏi gửi?

**Dễ trả lời sai:** "Nên, path `.satisfied` thì gửi, không thì báo offline luôn."

**Nên trả lời:** Reachability chỉ là gợi ý: path `.satisfied` vẫn có thể là Wi-Fi captive portal hoặc server đang sập, còn trạng thái "không có mạng" có thể thay đổi ngay sau khi bạn kiểm tra. Apple khuyến nghị cứ thử request rồi xử lý lỗi, và bật `waitsForConnectivity = true` để `URLSession` tự chờ khi có mạng. `NWPathMonitor` hữu ích để kích hoạt flush sync queue hoặc cập nhật UI, không phải để làm cổng chặn request.

### Lưu sync queue trong memory hoặc `UserDefaults` được không?

**Dễ trả lời sai:** "Được, queue nhỏ thôi, lưu tạm rồi gửi khi có mạng."

**Nên trả lời:** Memory mất khi app bị kill, còn `UserDefaults` không có transaction nên thay đổi local và bản ghi trong queue có thể lệch nhau nếu app crash giữa chừng. Queue nên nằm trong cùng database với dữ liệu và được ghi trong cùng transaction. Kể cả vậy, xóa app là mất toàn bộ container, nên các write chưa sync sẽ mất theo — cần cho user thấy trạng thái "chưa đồng bộ".

### Last-write-wins dựa trên timestamp của thiết bị có đủ để giải quyết conflict không?

**Dễ trả lời sai:** "Đủ, bản ghi nào có `updatedAt` mới hơn thì thắng."

**Nên trả lời:** Đồng hồ thiết bị có thể sai hoặc bị user chỉnh, nên "mới hơn" không đáng tin, và LWW âm thầm làm mất thay đổi của một bên. Cách an toàn hơn là để server cấp version hoặc `ETag`; client gửi kèm `If-Match`, server trả `412 Precondition Failed` nếu dữ liệu đã đổi, rồi app quyết định merge hoặc hỏi user. LWW chỉ chấp nhận được với dữ liệu ít quan trọng như settings.

## Bài tập

Thiết kế offline-first feed screen trong pseudocode/comment: (1) load từ cache → hiển thị ngay, (2) fetch từ network trong background → merge và refresh UI, (3) khi network lỗi → giữ cached data + hiển thị non-blocking banner "Cập nhật lần cuối X". Xác định: tầng nào sở hữu cache reads/writes, tầng nào quyết định hiển thị stale banner, và điều gì xảy ra với queued write nếu người dùng xóa và cài lại app.
