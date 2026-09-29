[← Docs](../README.md)

# Bản đồ kiến thức iOS

Bảng freeform (kéo thả, zoom) gồm toàn bộ chủ đề trong lộ trình 10 ngày. Nội dung được sinh từ source, không nhập tay.

| File | Vai trò |
| --- | --- |
| `index.html` | Giao diện bảng. Mở trực tiếp bằng trình duyệt. |
| `data.js` | Dữ liệu tự sinh. Đừng sửa tay. |
| `build.py` | Đọc `PROGRESS.vi.md` và các file `.vi.md`, sinh ra `data.js`. |

## Dữ liệu lấy từ đâu

- **Nhóm và thứ tự chủ đề:** các mục `## Ngày N — ...` trong `PROGRESS.vi.md`.
- **Đã nắm hay chưa:** checkbox `[x]` trong `PROGRESS.vi.md`.
- **Nội dung từng note** (từ file chủ đề `.vi.md`), chia thành 4 tab:
  - **Bài học:** toàn bộ các mục `##` của bài, kể cả ví dụ code và bảng.
  - **Hỏi & đáp:** mục `## Đáp án câu hỏi luyện tập`, mỗi `###` là một câu hỏi, bên dưới là câu trả lời. Đáp án được ẩn, bấm mới hiện.
  - **Bẫy phỏng vấn:** mục `## Bẫy phỏng vấn`, mỗi `###` là một bẫy, gồm `**Dễ trả lời sai:**` và `**Nên trả lời:**`.
  - **Bài tập:** mục `## Bài tập`.
- **Liên kết chéo:** danh sách `LINKS` trong `build.py`.

## Sử dụng

Sau khi sửa bất kỳ file bài học hoặc `PROGRESS`, chạy lại lệnh bên dưới. Script sẽ báo chủ đề nào còn thiếu đáp án hoặc bẫy.

```bash
python3 Docs/KnowledgeMap/build.py
```

Tick "Đã nắm" trên bảng chỉ lưu tạm trong trình duyệt. Bảng hiện hộp "thay đổi chưa ghi" kèm lệnh để ghi vào cả `PROGRESS.md` và `PROGRESS.vi.md`, ví dụ:

```bash
python3 Docs/KnowledgeMap/build.py --done Swift/Protocols --undone Swift/ARC
```

Chỉ cần Python 3, không cần cài thêm gì.
