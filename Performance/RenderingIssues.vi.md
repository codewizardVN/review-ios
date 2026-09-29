[English](./RenderingIssues.md) | [Tiếng Việt](./RenderingIssues.vi.md)

[← Performance](./README.vi.md)

# Hiệu năng Rendering

## Frame Budget

Ở 60fps, mỗi frame có ~16,7ms. Ở 120fps (ProMotion), ~8,3ms. Trong khoảng thời gian đó, cả phần việc của app trên main thread (xử lý event, layout, vẽ, commit) lẫn phần việc của render server trên GPU (ghép các layer) phải xong. Nếu một trong hai chặng vượt budget, frame bị trễ (hitch) và màn hình phải hiển thị lại frame cũ.

## Vấn đề phổ biến

| Vấn đề | Nguyên nhân | Giải pháp |
| --- | --- | --- |
| Offscreen rendering | Clip nội dung/sublayer bằng `cornerRadius` + `masksToBounds`, dùng `mask`, shadow không có `shadowPath`, group opacity | Set `shadowPath` cho shadow; chỉ bật `masksToBounds` khi thật sự cần clip nội dung (nếu chỉ cần bo nền thì `cornerRadius` một mình là đủ); với ảnh có thể bo góc sẵn khi decode |
| Blending | View trong suốt chồng lên nhau, GPU phải trộn màu từng pixel | Dùng `backgroundColor` đục và `alpha = 1` khi có thể (`isOpaque = true` chỉ là gợi ý cho việc vẽ, không tự làm view đục) |
| Image decode trên main thread | Ảnh lớn load đồng bộ | Decode ở background, hiển thị trên main |
| `body` tính toán nặng | Logic nặng trong SwiftUI `body` | Tách ra ViewModel, memoize |

## Công cụ phát hiện

- **Instruments → Animation Hitches** — cho biết frame nào bị trễ, trễ bao lâu và là commit hitch hay render hitch (đây là công cụ chính hiện nay; các tuỳ chọn tô màu của instrument Core Animation cũ đã được chuyển sang Xcode/Simulator)
- **Color Blended Layers** — highlight chi phí transparency (xanh = không blending, đỏ = có blending)
- **Color Offscreen-Rendered** — highlight layer bị render offscreen (vàng)
- Hai tuỳ chọn tô màu trên nằm trong menu Debug của Simulator, hoặc khi chạy trên thiết bị thật: Xcode → Debug → View Debugging → Rendering

## Câu hỏi thực hành

- Tại sao UI bị dropped frame?
- Tại sao image loading có thể khiến app cảm thấy giật?

## Câu hỏi luyện tập

- Tại sao UI bị rớt frame?
- Tại sao việc load ảnh có thể khiến app cảm giác giật lag?

## Góc nhìn senior

Trả lời theo quy trình: quan sát triệu chứng, mở Instruments, isolate layer gây dropped frame, đo chi phí thực tế trước khi tối ưu. Không đoán mò.

## Đáp án câu hỏi luyện tập

### Tại sao UI bị rớt frame?

UI rớt frame khi một frame không kịp hoàn thành trước deadline của màn hình (khoảng 16,7ms ở 60Hz, 8,3ms ở 120Hz ProMotion), nên màn hình phải hiển thị lại frame cũ — người dùng thấy giật, Apple gọi đó là hitch. Mỗi frame đi qua hai chặng chính:

- **Commit trong app, trên main thread:** xử lý event, chạy code của bạn, layout (Auto Layout, `layoutSubviews`, SwiftUI `body`), vẽ (`draw(_:)`), decode ảnh, rồi gửi layer tree sang render server. Nếu main thread bận (decode JSON, I/O đồng bộ, layout phức tạp) thì commit bị trễ — gọi là commit hitch.
- **Render trong render server (process riêng, dùng GPU):** ghép (composite) các layer thành ảnh cuối. Nếu layer tree quá nặng — nhiều offscreen pass do mask hay `cornerRadius` + `masksToBounds`, shadow không có `shadowPath`, nhiều lớp trong suốt chồng nhau (blending), blur — GPU không kịp, gọi là render hitch.

Phân biệt hai loại này quan trọng vì cách sửa khác nhau: commit hitch sửa bằng cách bớt việc trên main thread; render hitch sửa bằng cách đơn giản hoá layer. Dùng template Animation Hitches trong Instruments để xem frame nào trễ và trễ ở chặng nào, rồi dùng Time Profiler hoặc Color Offscreen-Rendered / Color Blended Layers để tìm nguyên nhân cụ thể. Trade-off: đừng theo phản xạ xoá hết shadow và bo góc; chỉ tối ưu những layer thật sự nằm trong frame bị trễ.

### Tại sao việc load ảnh có thể khiến app cảm giác giật lag?

Vì ảnh phải được decode từ dữ liệu nén (JPEG/PNG/HEIC) thành bitmap trước khi hiển thị, và mặc định việc này diễn ra "lười" trên main thread đúng lúc ảnh được render lần đầu. `UIImage(named:)` hay `UIImage(data:)` chỉ tạo object bọc dữ liệu nén; khi gán vào `UIImageView` và Core Animation commit, ảnh mới được decode — trên main thread, trong chính frame đó. Một ảnh 12MP (4032×3024) decode ra bitmap khoảng 4032 × 3024 × 4 byte ≈ 48MB và có thể mất hàng chục ms, vượt budget của frame. Trong list, mỗi cell mới hiện ra là một lần decode nữa, nên scroll khựng và memory tăng vọt (có thể bị hệ thống kill vì hết memory).

Cách sửa:

- Downsample về đúng kích thước hiển thị bằng ImageIO (`CGImageSourceCreateThumbnailAtIndex`) hoặc `UIImage.preparingThumbnail(of:)` (iOS 15+).
- Decode sẵn ở background bằng `byPreparingForDisplay()` / `prepareForDisplay(completionHandler:)` (iOS 15+), rồi mới gán trên main.
- Cache ảnh đã decode (ví dụ `NSCache`) và cancel request khi cell bị reuse (trong `prepareForReuse`).
- Không đọc file hay network đồng bộ trên main.

Trade-off: bitmap đã decode tốn memory hơn dữ liệu nén rất nhiều, nên cache cần giới hạn. SwiftUI `AsyncImage` tiện nhưng không cho bạn downsample và không có cache ảnh đã decode (chỉ dựa vào HTTP cache của `URLSession`), nên thường không đủ cho list ảnh lớn.

## Bẫy phỏng vấn

### "`cornerRadius` luôn gây offscreen rendering, đúng không?"

**Dễ trả lời sai:** Cứ set `cornerRadius` là bị offscreen, nên phải tránh bo góc bằng layer.

**Nên trả lời:** `cornerRadius` một mình chỉ bo background và border của layer, GPU vẽ trực tiếp mà không cần offscreen pass. Offscreen thường xuất hiện khi phải clip cả nội dung và sublayer (`masksToBounds = true` với nhiều sublayer), khi dùng `mask`, shadow không có `shadowPath`, hoặc group opacity. Đừng khẳng định theo trí nhớ — bật Color Offscreen-Rendered và kiểm tra thực tế.

### "Để sửa `CardView`, chỉ cần giữ `masksToBounds` và thêm `shadowPath` trên cùng layer?"

**Dễ trả lời sai:** Đặt shadow, `shadowPath` và `masksToBounds = true` trên cùng một layer là được.

**Nên trả lời:** `masksToBounds` cắt mọi thứ nằm ngoài bounds, kể cả shadow, nên hai thứ này không thể cùng nằm trên một layer. Nếu nội dung (ví dụ ảnh) cần được clip theo bo góc, tách thành hai view: container ngoài có shadow + `shadowPath`, view bên trong có `cornerRadius` + `masksToBounds`. Và `shadowPath` phải được cập nhật trong `layoutSubviews` khi bounds đổi, nếu không bóng sẽ sai kích thước.

```swift
layer.shadowPath = UIBezierPath(roundedRect: bounds, cornerRadius: 12).cgPath
```

### "Simulator chạy 60fps mượt, vậy là ổn?"

**Dễ trả lời sai:** Đo FPS trên simulator hoặc debug build là đủ để kết luận về rendering.

**Nên trả lời:** Simulator render bằng GPU và CPU của Mac nên không phản ánh thiết bị thật; debug build lại chậm hơn release. FPS cũng là chỉ số kém, vì khi màn hình đứng yên FPS thấp là bình thường. Apple dùng hitch time ratio (số ms bị trễ trên mỗi giây animation/scroll). Đo trên thiết bị thật, release build, ưu tiên máy yếu nhất bạn hỗ trợ, và nhớ rằng ProMotion chỉ cho khoảng 8ms mỗi frame.

## Bài tập

Lấy `CardView` dùng `cornerRadius` với `masksToBounds` và shadow. Bật "Color Offscreen-Rendered" (menu Debug của Simulator, hoặc Xcode → Debug → View Debugging → Rendering trên thiết bị) và xác nhận highlight vàng xuất hiện. Sửa bằng cách set `shadowPath` rõ ràng (cập nhật trong `layoutSubviews`) và xóa `masksToBounds`; nếu nội dung bên trong vẫn cần được clip theo bo góc, tách thành container có shadow và view con có `cornerRadius` + `masksToBounds` như trong Bẫy phỏng vấn. Xác minh màu vàng biến mất, rồi đo lại bằng Animation Hitches trên thiết bị thật.
