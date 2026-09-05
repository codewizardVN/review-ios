[English](./Accessibility.md) | [Tiếng Việt](./Accessibility.vi.md)

[← Accessibility và Localization](./README.vi.md)

# Accessibility

## Ý chính

Accessibility không chỉ là một checkbox VoiceOver. Đó là việc giao diện có còn hoạt động hay không khi một kênh input/output nào đó bị suy giảm — thị giác, thính giác, khả năng vận động, hay khả năng đọc — và nó được test bằng cách thực sự dùng app theo cách đó, chứ không phải bằng cách đọc code.

## Những điều cần nắm

- VoiceOver cơ bản — `accessibilityLabel`, `accessibilityValue`, `accessibilityHint`, `accessibilityTraits`; label mô tả *cái gì*, value mô tả *trạng thái*, hint mô tả *chuyện gì xảy ra nếu kích hoạt*
- Gom nhóm và thứ tự đọc — `accessibilityElement(children:)`, thứ tự traversal tùy chỉnh (`accessibilitySortPriority` / `accessibilityElements`) để VoiceOver đọc nội dung theo thứ tự hợp lý, không theo thứ tự DOM/z-order
- Dynamic Type — `.font(.body)` với text style hệ thống tự scale; point size cố định thì không; layout phải reflow, không chỉ bị cắt, ở các cỡ accessibility (tới `.accessibility5`)
- Custom action — `accessibilityActions` / `UIAccessibilityCustomAction` để expose các gesture chỉ có swipe (ví dụ "delete", "archive") cho user VoiceOver không thể swipe trên một cell
- Reduce Motion / Reduce Transparency — `UIAccessibility.isReduceMotionEnabled`, được check trước khi chạy animation không cần thiết hoặc hiệu ứng parallax
- Color contrast và "đừng chỉ dựa vào màu" — kết hợp trạng thái mã hóa bằng màu với icon hoặc text label cho user mù màu
- Quản lý focus — di chuyển VoiceOver focus (`UIAccessibility.post(notification: .screenChanged, argument:)`) sau khi một sheet hiện lên hoặc list được cập nhật, để focus không bị "mắc kẹt" âm thầm
- Accessibility Inspector và công cụ Audit trong Xcode — check tự động (contrast, thiếu label, kích thước vùng tap) như một bước sàng lọc đầu, không thay thế cho việc test VoiceOver thủ công

## Ví dụ

```swift
Button {
    toggleFavorite()
} label: {
    Image(systemName: isFavorite ? "heart.fill" : "heart")
}
.accessibilityLabel("Favorite")
.accessibilityValue(isFavorite ? "On" : "Off")
.accessibilityAddTraits(.isButton)
```

## Câu hỏi luyện tập

- Tại sao `accessibilityLabel("Heart icon")` cho một nút favorite là một label tệ?
- Điều gì bị gãy trong một cell thiết kế chiều cao cố định khi user đặt cỡ Dynamic Type lớn nhất?
- Tại sao một biểu đồ tự vẽ (Canvas/Core Graphics) cần công sức accessibility tường minh mà một `List` gốc được miễn phí?

## Góc nhìn Senior

Câu hỏi accessibility phân biệt người đã thực sự bật VoiceOver lên dùng với người chỉ đọc về `accessibilityLabel`. Tín hiệu tốt là mô tả một lỗi cụ thể bạn tìm thấy khi test bằng VoiceOver hoặc ở Dynamic Type lớn nhất — một control không tới được, một label đọc sai, một layout bị cắt — và cách fix đã thay đổi cấu trúc view bên dưới, chứ không chỉ thêm label như một việc làm thêm sau cùng.

## Bài tập

Lấy một component card tùy chỉnh hiển thị ảnh sản phẩm, tên, giá, giá gốc gạch ngang, và badge "giảm 20%" là một ribbon màu ở góc. Nêu rõ: thứ tự đọc VoiceOver và label/value gộp lại, giảm giá được truyền tải ra sao mà không chỉ dựa vào màu của ribbon, cái gì thay đổi ở cỡ Dynamic Type lớn nhất, và một custom action bạn sẽ thêm cho user VoiceOver tương đương với gesture vuốt mà user sáng mắt có.
