[English](./ReleaseProcess.md) | [Tiếng Việt](./ReleaseProcess.vi.md)

[← Chủ đề Senior](./README.vi.md)

# Release Process

## Senior nên nói tới gì

- kiểm soát scope và tiêu chí release
- feature flag và kill switch
- QA, smoke test, và monitoring
- rollback hoặc mitigation plan

## Luồng điển hình

1. Chốt scope cho release candidate.
2. Chạy regression có trọng tâm ở các vùng rủi ro cao.
3. Xác nhận analytics, logging, và crash reporting đã sẵn sàng.
4. Rollout dần nếu có thể.
5. Theo dõi crash, funnel quan trọng, và tình trạng backend.

## Câu hỏi thực hành

- Điều gì khiến bạn chặn một release?
- Làm sao giảm release risk khi deadline đã cố định?

## Góc nhìn senior

Release là một kỷ luật vận hành, không chỉ là bấm nút trên App Store Connect. Câu trả lời tốt nhất cân bằng tốc độ delivery với các guardrail đủ mạnh để team phục hồi nhanh khi có sự cố.

## Bài tập

Team buộc phải ship một update cho payments trước chiến dịch marketing. Hãy lập một release checklist gồm pre-release checks, rollout strategy, monitoring signal, và stop-ship criteria.
