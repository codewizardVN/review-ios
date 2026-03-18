[English](./ProductionDebugging.md) | [Tiếng Việt](./ProductionDebugging.vi.md)

[← Chủ đề Senior](./README.vi.md)

# Debug vấn đề Production

## Quy trình

```text
1. Observe — crash log, tỷ lệ lỗi, báo cáo người dùng
2. Reproduce — có thể reproduce ở local hay staging không?
3. Isolate — build nào, OS version, loại device, phân khúc người dùng?
4. Fix — thay đổi có mục tiêu với blast radius tối thiểu
5. Verify — deploy, theo dõi metrics, xác nhận đã giải quyết
```

## Công cụ

- **Firebase Crashlytics / Sentry** — symbolication và nhóm crash
- **dSYM files** — cần thiết cho crash log có symbol; archive và upload mỗi lần release
- **MetricKit** — dữ liệu hiệu năng và crash trên thiết bị
- **TestFlight** — phân phối debug build để reproduce vấn đề

## Vấn đề chỉ xảy ra trong Production

- Race condition xuất hiện dưới tải thật
- Memory pressure trên thiết bị cũ
- Edge case về localization hoặc timezone
- API contract thay đổi không được phát hiện trong development

## Câu hỏi thực hành

- Bạn tiếp cận một crash production ngẫu nhiên như thế nào?

## Góc nhìn senior

Crash production không có đường reproduce đòi hỏi xây dựng giả thuyết từ dữ liệu có sẵn: stack trace, phân phối OS/device, phạm vi app version, cohort người dùng. Thu hẹp không gian giả thuyết trước khi viết bất kỳ fix nào.

## Bài tập

Cho một báo cáo Crashlytics cho thấy crash force-unwrap `nil` trong `CartViewController.viewDidLoad` chỉ ảnh hưởng người dùng iOS 16 trên version 2.3.1: viết toàn bộ quy trình debug của bạn — những giả thuyết nào bạn đặt ra, dữ liệu nào cần thu thập tiếp, và chiến lược fix trông như thế nào trước khi reproduce được ở local.
