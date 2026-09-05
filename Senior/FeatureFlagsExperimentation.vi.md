[English](./FeatureFlagsExperimentation.md) | [Tiếng Việt](./FeatureFlagsExperimentation.vi.md)

[← Chủ đề cấp Senior](./README.vi.md)

# Feature Flags và Experimentation

## Ý chính

Một feature flag là một nhánh runtime tồn tại lâu hơn cả PR đã thêm nó, trừ khi có ai đó chủ động xóa nó đi. Coi flag là miễn phí chính là cách một codebase tích lũy logic điều kiện rối rắm, vĩnh viễn mà không ai dám xóa.

## Những điều cần nắm

- Các loại flag — release flag (tạm thời, gate một feature đang làm dở), ops/kill-switch flag (vĩnh viễn, tắt một feature rủi ro khi tải cao hoặc gặp sự cố), permission flag (dựa trên entitlement), experiment flag (gán variant cho A/B test)
- Remote config vs local build flag — flag cấu hình từ xa có thể đổi hành vi mà không cần submit App Store mới, đổi lại phải định nghĩa rõ hành vi mặc định khi offline/cache-miss
- Cơ chế A/B test — gán variant (thường là hash ổn định của user ID, không phải random mỗi session), sample ratio mismatch như một tín hiệu cho thấy randomization đang bị lỗi, guardrail metric có thể tự động abort một experiment
- Cơ bản về tính hợp lệ thống kê — tại sao nhìn trộm kết quả sớm và dừng ngay khi thấy "có vẻ significant" làm tăng false positive, và tại sao sample size phải được quyết định trước khi bắt đầu
- Vòng đời và dọn dẹp flag — mỗi release flag cần một owner và một ngày xóa; một flag còn sót trong code sau khi đã rollout toàn bộ là gánh nặng chết và nguồn gốc của bug kiểu "sao nhánh này còn tồn tại"
- Test dưới các flag — một flag nhân lên tổ hợp trạng thái app; quyết định tổ hợp nào thực sự đáng test (thường là: trạng thái mặc định, từng flag bật riêng lẻ, không phải tích đầy đủ)
- Rủi ro phía client — SDK flag bị outage hoặc fetch chậm phải có default an toàn; một feature fail open (bật) khi lẽ ra phải fail closed (tắt) là một sự cố production phổ biến
- Nhất quán UI theo flag — user không nên thấy một feature "nhấp nháy" bật lên giữa session vì flag vừa re-fetch; trạng thái flag thường được snapshot theo mỗi session/lần mở app

## Ví dụ

```swift
enum PaywallVariant { case control, redesign }

func paywallVariant(for userId: String) -> PaywallVariant {
    // Bucketing dựa trên hash ổn định — cùng một user luôn rơi vào cùng một variant
    let bucket = stableHash(userId) % 100
    return bucket < 50 ? .control : .redesign
}
```

## Câu hỏi luyện tập

- Tại sao gán variant random mỗi session thường là sai cho một A/B test?
- Chuyện gì nên xảy ra nếu network call fetch flag fail lúc cold launch?
- Tại sao một release flag "tạm thời" từ sáu tháng trước được tính là tech debt?

## Góc nhìn Senior

Tín hiệu phỏng vấn ở đây là ai đó đã thực sự chịu trách nhiệm dọn dẹp mớ hỗn độn mà hệ thống flag tạo ra theo thời gian, chứ không chỉ dùng nó. Câu trả lời tốt nêu được một failure mode cụ thể: một experiment ship ra false positive vì ai đó dừng sớm, một kill-switch fail open trong lúc sự cố vì default không được đặt phòng thủ, hoặc một codebase với hàng chục release flag không ai nhớ mục đích. Cách fix trong mỗi trường hợp là quy trình (ownership của flag, ngày xóa, guardrail metric), không chỉ là "chúng tôi dùng LaunchDarkly."

## Bài tập

Thiết kế setup flag và experimentation để test một luồng onboarding mới so với luồng hiện tại. Nêu rõ: loại flag và cách variant được bucket, chuyện gì xảy ra ở lần mở đầu tiên nếu remote config chưa fetch xong, một guardrail metric sẽ tự động abort experiment, và kế hoạch của bạn (owner, deadline, điều kiện) để xóa flag khi đã có kết quả thắng.
