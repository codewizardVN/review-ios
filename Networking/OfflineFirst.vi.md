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

- `NWPathMonitor` — theo dõi network reachability
- Optimistic UI — áp dụng thay đổi local trước khi server xác nhận
- Sync queue — queue write khi offline, flush khi có mạng trở lại
- Conflict resolution — last-write-wins, server-wins, hoặc merge

## Câu hỏi thực hành

- Nếu API chậm hoặc không ổn định, bạn sẽ thiết kế data flow như thế nào?

## Góc nhìn Senior

Offline-first là quyết định UX trước khi là quyết định kỹ thuật. Định nghĩa "offline" có nghĩa gì với từng tính năng: chỉ đọc cache? Cho phép write? Hiển thị staleness indicator? Căn chỉnh với product trước khi xây dựng sync layer.

## Bài tập

Thiết kế offline-first feed screen trong pseudocode/comment: (1) load từ cache → hiển thị ngay, (2) fetch từ network trong background → merge và refresh UI, (3) khi network lỗi → giữ cached data + hiển thị non-blocking banner "Cập nhật lần cuối X". Xác định: tầng nào sở hữu cache reads/writes, tầng nào quyết định hiển thị stale banner, và điều gì xảy ra với queued write nếu người dùng xóa và cài lại app.
