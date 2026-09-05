[English](./CrashReportingAnalytics.md) | [Tiếng Việt](./CrashReportingAnalytics.vi.md)

[← Chủ đề cấp Senior](./README.vi.md)

# Crash Reporting và Analytics

## Ý chính

Một SDK crash reporting/analytics là hạ tầng production, không phải một thư viện import cho có. Câu hỏi cấp senior xoay quanh tính đúng đắn của symbolication, kỷ luật schema sự kiện, và privacy — không phải dashboard vendor nào đẹp hơn.

## Những điều cần nắm

- Pipeline symbolication — upload dSYM (thủ công hoặc qua script build-phase), khớp UUID dSYM với đúng build đã crash; dSYM sai hoặc thiếu biến crash report thành các địa chỉ bộ nhớ không đọc được
- Crash-free rate như một release gate — theo dõi phần trăm user/session không crash theo từng version, và ngưỡng nào chặn không cho rollout tiếp tục
- Symbolicate trên thiết bị vs server-side — tại sao chỉ dựa vào Organizer của Xcode không scale được, và tại sao pipeline CI nên tự động upload dSYM ở mỗi lần archive
- Breadcrumb và log non-fatal — ghi lại dấu vết các hành động/state gần nhất của user trước một crash hoặc lỗi đã handle, để report có ngữ cảnh ngoài stack trace
- Kỷ luật schema sự kiện — tên event có version và payload có kiểu, tránh property free-text làm phân mảnh analytics ("purchase_completed" vs "PurchaseComplete" vs "purchase-done" đều nghĩa giống nhau)
- Sampling và chi phí — event tần suất cao (ví dụ vị trí scroll) thường cần sampling hoặc gộp phía client; gửi mọi raw event thường là gánh nặng chi phí và privacy chứ không phải lợi ích
- Ranh giới privacy — cái gì không được đưa vào payload event (PII, vị trí chính xác, nội dung free-text của user) và điều đó ràng buộc thiết kế schema ra sao, gắn với những gì privacy manifest và nutrition label đã khai
- Ngưỡng alert — bộ phát hiện đột biến trên crash rate hay một metric funnel quan trọng, được tinh chỉnh để vừa tránh alert fatigue vừa không bỏ lỡ regression thật

## Ví dụ

```swift
// Tệ: free-text, không version, không ngữ cảnh
Analytics.log("bought item")

// Tốt hơn: có kiểu, có version, mang ngữ cảnh cho một "lý do" mà không có PII
Analytics.log(event: .purchaseCompleted(
    sku: "premium_monthly",
    priceTierCents: 999,
    source: .paywallVariantB
))
```

## Câu hỏi luyện tập

- Tại sao một dSYM bị thiếu quan trọng hơn một dòng comment code bị thiếu?
- Tại sao "crash-free users" thường là release gate tốt hơn số crash thô?
- Tại sao tên event analytics nên được review như một API, chứ không thêm tùy tiện theo từng feature?

## Góc nhìn Senior

Đây là chỗ mà "chúng tôi đã cài Crashlytics" và "chúng tôi thực sự hành động được dựa trên tín hiệu production" khác nhau. Câu trả lời tốt mô tả một sự cố mà nợ symbolication hoặc schema event đã thực sự làm chậm việc debug — một crash report không đọc được, một metric không ai tin tưởng vì ba team log cùng một event khác nhau — và quy trình nào (review schema, tự động upload dSYM trong CI, release gate gắn với crash-free rate) đã fix nó một cách có hệ thống thay vì chỉ vá tạm.

## Bài tập

Thiết kế rollout crash-reporting và analytics cho một luồng checkout mới. Nêu rõ: những event non-fatal nào bạn sẽ log và schema của chúng (có tính đến ràng buộc privacy), dSYM được upload tự động thế nào trong pipeline CI/CD, ngưỡng crash-free-rate nào sẽ dừng một phased rollout, và một tình huống debug mà thiếu breadcrumb sẽ khiến bạn không thể chẩn đoán một bug chỉ xảy ra ở production.
