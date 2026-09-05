[English](./Day10_Platform_Quality_Growth.md) | [Tiếng Việt](./Day10_Platform_Quality_Growth.vi.md)

# Ngày 10: Platform Quality và Growth

## Goal

Bao phủ các chủ đề thường bị bỏ qua ở lần ôn đầu tiên nhưng sẽ xuất hiện khi app có user thật: accessibility, localization, interop với legacy, hành vi background, widget ở các bề mặt hệ thống, và bộ máy App Store/analytics/experimentation xoay quanh việc ship sản phẩm.

## Topics

- Accessibility (VoiceOver, Dynamic Type)
- Localization và internationalization
- Objective-C interop
- Background execution (`BGTaskScheduler`, background URLSession)
- Widgets và Live Activities
- App Store submission và review
- Crash reporting và analytics
- Feature flags và experimentation

## What You Should Be Able To Explain

- Cách bạn test một màn hình bằng VoiceOver và ở cỡ Dynamic Type lớn nhất, và thứ gì thường bị gãy
- Tại sao layout, quy tắc số nhiều, và độ dài text mở rộng là vấn đề của localization, không chỉ là dịch thuật
- Feature nào của Swift không sống sót khi bắc cầu sang Objective-C, và tại sao
- Tại sao background execution phải được coi là best-effort, không bao giờ đảm bảo
- Tại sao một widget hay Live Activity là một process riêng biệt, không phải một view sống động vào app của bạn
- Điều gì gây ra các rejection App Store phổ biến nhất, và cách ngăn chúng trước khi submit
- Tại sao một dSYM bị thiếu hay schema event analytics không nhất quán tốn thời gian debug thật sự
- Tại sao một feature flag cần một owner và một ngày xóa, chứ không chỉ là một câu `if`

## Practice Questions

- App của bạn trông ổn về mặt hình ảnh nhưng fail khi test bằng VoiceOver — điều đầu tiên bạn kiểm tra là gì?
- Một build bị reject vì vấn đề privacy manifest mà bạn không biết là nó tồn tại — điều đó nói lên gì về release checklist của bạn?
- Một kill-switch flag bị fail "open" trong lúc sự cố — default của nó lẽ ra phải như thế nào?

## Senior Notes

- Các chủ đề này hiếm khi xuất hiện như một câu hỏi phỏng vấn riêng, nhưng chúng xuất hiện bên trong các câu hỏi system design và "kể về một sự cố production".
- Điểm chung xuyên suốt tất cả: có một thứ mà hệ thống, OS, hoặc quy trình review kiểm soát — chứ không phải app của bạn — quyết định kết quả, và một senior engineer thiết kế cho sự bất định đó thay vì giả định mình có quyền kiểm soát mà thực ra không có.
