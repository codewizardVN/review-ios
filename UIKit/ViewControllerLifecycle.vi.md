[English](./ViewControllerLifecycle.md) | [Tiếng Việt](./ViewControllerLifecycle.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# View Controller Lifecycle

## Ý chính

Mỗi lifecycle method có vai trò khác nhau. Bug thường xuất hiện khi networking, layout work, analytics, hoặc binding logic được đặt sai thời điểm.

## Cần ôn

- `viewDidLoad` cho setup một lần
- `viewWillAppear` cho state cần refresh trước khi hiển thị
- `viewDidAppear` cho tracking hoặc công việc cần view đã xuất hiện
- `viewDidDisappear` và thời điểm cleanup

## Câu hỏi thực hành

- `viewWillAppear` khác `viewDidAppear` ở điểm nào?
- Công việc nào không nên đặt trong `viewDidLoad`?

## Góc nhìn senior

Lifecycle thực chất là chuyện ownership và timing. Câu trả lời tốt cần giải thích vì sao một việc thuộc về phase đó, thay vì chỉ thuộc callback theo kiểu học thuộc.

## Bài tập

Review một controller đang gọi API trong `viewDidAppear`, set constraints trong `viewWillAppear`, và subscribe notification trong `viewDidLoad` mà không cleanup. Hãy chuyển từng trách nhiệm sang vị trí phù hợp hơn và giải thích lý do.
