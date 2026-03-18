[English](./BackwardCompatibility.md) | [Tiếng Việt](./BackwardCompatibility.vi.md)

[← Chủ đề Senior](./README.vi.md)

# Backward Compatibility

## Ý chính

Backward compatibility nghĩa là code mới không làm hỏng client cũ, dữ liệu đã persist, hoặc các OS version còn được hỗ trợ nếu chưa có migration plan rõ ràng.

## Cần ôn

- Thay đổi API contract và fallback behavior
- Migration cho database hoặc cache
- Feature flag để rollout theo giai đoạn
- Availability check theo OS và graceful degradation

## Ví dụ

Nếu server thêm một field bắt buộc, app version cũ có thể fail trừ khi decoding đủ tolerant hoặc backend hỗ trợ giai đoạn chuyển tiếp.

## Câu hỏi thực hành

- Làm sao ship feature mới mà vẫn hỗ trợ app version cũ?
- Khi nào bạn cần migration thay vì silent fallback?

## Góc nhìn senior

Compatibility không chỉ là chuyện kỹ thuật. Nó là product work. Một câu trả lời senior tốt sẽ nghĩ tới người dùng thật đang ở build cũ, staged release, và recovery path khi giả định bị sai trong production.

## Bài tập

Team muốn thay schema của local cache và ship thêm một bước onboarding mới trong cùng release. Hãy mô tả các compatibility risk và cách bạn sắp rollout an toàn.
