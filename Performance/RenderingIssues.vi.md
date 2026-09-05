[English](./RenderingIssues.md) | [Tiếng Việt](./RenderingIssues.vi.md)

[← Performance](./README.vi.md)

# Hiệu năng Rendering

## Frame Budget

Ở 60fps, mỗi frame có ~16ms. Ở 120fps (ProMotion), ~8ms. Bất kỳ công việc nào trên main thread vượt quá budget này sẽ gây dropped frame.

## Vấn đề phổ biến

| Vấn đề | Nguyên nhân | Giải pháp |
| --- | --- | --- |
| Offscreen rendering | `cornerRadius` + `masksToBounds`, shadow không có `shadowPath` | Set `shadowPath`, dùng `CAShapeLayer` |
| Blending | Transparent view composited chồng lên nhau | Set `isOpaque = true`, tránh alpha khi có thể |
| Image decode trên main thread | Ảnh lớn load đồng bộ | Decode ở background, hiển thị trên main |
| `body` tính toán nặng | Logic nặng trong SwiftUI `body` | Tách ra ViewModel, memoize |

## Công cụ phát hiện

- **Core Animation instrument** — hiển thị frame rate và offscreen rendering pass
- **Debug → Color Blended Layers** — highlight chi phí transparency (xanh = ok, đỏ = blending)
- **Debug → Color Offscreen-Rendered** — highlight GPU offscreen pass (vàng)

## Câu hỏi thực hành

- Tại sao UI bị dropped frame?
- Tại sao image loading có thể khiến app cảm thấy giật?

## Câu hỏi luyện tập

- Tại sao UI bị rớt frame?
- Tại sao việc load ảnh có thể khiến app cảm giác giật lag?

## Góc nhìn senior

Trả lời theo quy trình: quan sát triệu chứng, mở Instruments, isolate layer gây dropped frame, đo chi phí thực tế trước khi tối ưu. Không đoán mò.

## Bài tập

Lấy `CardView` dùng `cornerRadius` với `masksToBounds` và shadow. Bật "Color Offscreen-Rendered" trong simulator và xác nhận highlight vàng xuất hiện. Sửa bằng cách set `shadowPath` rõ ràng và xóa `masksToBounds`. Xác minh màu vàng biến mất.
